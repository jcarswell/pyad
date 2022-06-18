from typing import List
from .adobject import ADObject
from . import pyadutils
from . import pyadconstants


class ADGroup(ADObject):
    """
    The class representing Active Directory groups and the accessors methods specific
    to groups.
    """

    @classmethod
    def create(
        cls,
        name,
        container_object,
        security_enabled=True,
        scope="GLOBAL",
        optional_attributes={},
    ):
        """Creates and returns a new group"""
        return container_object.create_group(
            name=name,
            security_enabled=security_enabled,
            scope=scope,
            optional_attributes=optional_attributes,
        )

    def add_members(self, members):
        """
        Accepts a list of pyAD objects or a single pyAD object and adds as members to the
        group.
        """

        members = [member.dn for member in pyadutils.generate_list(members)]
        self.append_to_attribute("member", members)

    def remove_members(self, members: ADObject) -> None:
        """
        Accepts a list of pyAD objects or a single pyAD object and removes these as
        members from the group.
        """

        members = [member.dn for member in pyadutils.generate_list(members)]
        self.remove_from_attribute("member", members)

    def remove_all_members(self) -> None:
        """Removes all members of the group."""

        self.remove_from_attribute("member", self.get_attribute("member"))

    def get_members(
        self, recursive: bool = False, ignore_groups: bool = False
    ) -> List[ADObject]:
        """
        Returns a list of group members.

        :param recursive: Whether to recursively traverse through nested groups, defaults
            to False
        :type recursive: bool, optional
        :param ignore_groups: include groups in the list, defaults to False
        :type ignore_groups: bool, optional
        :return: _description_
        :rtype: List[ADObject]
        """

        return self._get_members(recursive, ignore_groups)

    def _get_members(
        self,
        recursive: bool,
        ignore_groups: bool = False,
        processedGroups: List[str] = [],
    ) -> List[ADObject]:
        """
        returns a list of pyAD objects that are members of the group.

        :param recursive: Whether to recursively traverse through nested groups, defaults
            to False
        :type recursive: bool
        :param ignore_groups: include groups in the list, defaults to False
        :type ignore_groups: bool, optional
        :param processedGroups: A list of object IDs that have already been processed,
            defaults to []
        :type processedGroups: List[str]
        :return: The members of the group
        :rtype: List[ADObject]
        """

        processedGroups.append(self.guid)
        # we need to keep track of which groups have been enumerated so far so that
        # we don't enter an infinite loop accidentally if group A is a member
        # of group B and group B is a member of group A. Yes, this can actually happen.
        ret = []
        for dn in self.get_attribute("member"):
            pyADobj = ADObject(dn, options=self._make_options())
            pyADobj.adjust_pyad_type()
            if pyADobj.type == "group" and pyADobj.guid not in processedGroups:
                if recursive:
                    ret.extend(
                        pyADobj._get_members(
                            recursive=True,
                            ignoreGroups=ignore_groups,
                            processedGroups=processedGroups,
                        )
                    )
                if not ignore_groups:
                    ret.append(pyADobj)
            elif pyADobj.type != "group":
                ret.append(pyADobj)
        return list((set(ret)))  # converting to set removes duplicates

    def sync_membership(self, new_population: List[ADObject]) -> None:
        """
        Synchronizes membership of group so that it matches the list of entries in new_population

        :param new_population: The list of entries to match against the group
        :type new_population: List[ADObject]
        """

        current_members = set(self.get_members())
        new_population = set(new_population)
        self.add_members(list(new_population - current_members))
        self.remove_members(list(current_members - new_population))

    def check_contains_member(
        self, check_member: ADObject, recursive: bool = False
    ) -> bool:
        """
        Checks whether the check_member is a member of the group

        :param check_member: The object to check for membership of the current group object
        :type check_member: ADObject
        :param recursive: Whether to recursively check membership or only check direct
            members, defaults to False
        :type recursive: bool, optional
        :return: Whether the check_member is a member of the group
        :rtype: bool
        """

        if check_member in self.get_members(recursive=recursive, ignoreGroups=False):
            return True
        else:
            return False

    def get_group_scope(self) -> str:
        """Returns the group scope GLOBAL, UNIVERSAL, or LOCAL."""
        group_type = self.get_attribute("groupType", False)
        c_global = pyadconstants.ADS_GROUP_TYPE["GLOBAL"]
        c_universal = pyadconstants.ADS_GROUP_TYPE["UNIVERSAL"]
        if group_type & pyadconstants.ADS_GROUP_TYPE["GLOBAL"] == c_global:
            return "GLOBAL"
        elif group_type & pyadconstants.ADS_GROUP_TYPE["UNIVERSAL"] == c_universal:
            return "UNIVERSAL"
        else:
            return "LOCAL"

    def set_group_scope(self, new_scope: str) -> None:
        """
        Sets group scope

        :param new_scope: The new group scope.
        :type new_scope: str ["GLOBAL", "UNIVERSAL", "LOCAL"]
        :raises ValueError: If new_scope is not valid
        """

        if new_scope in ("LOCAL", "GLOBAL", "UNIVERSAL"):
            self.update_attribute(
                "groupType",
                (
                    self.get_attribute("groupType", False)
                    & pyadconstants.ADS_GROUP_TYPE["SECURITY_ENABLED"]
                )
                | pyadconstants.ADS_GROUP_TYPE[new_scope],
            )
        else:
            raise ValueError("new_scope", new_scope, ("LOCAL", "GLOBAL", "UNIVERSAL"))

    def get_group_type(self) -> str:
        """Returns group type DISTRIBUTION or SECURITY."""
        # 0x2, 0x4, 0x8 are the distribution group types since
        # a security group must include -0x80000000.
        if self.get_attribute("groupType", False) in (2, 4, 8):
            return "DISTRIBUTION"
        else:
            return "SECURITY"

    def set_group_type(self, new_type: str) -> None:
        """
        Sets group type

        :param new_type: the new group type
        :type new_type: str ['DISTRIBUTION', 'SECURITY']
        :raises ValueError: new_type is not a valid group type
        """

        if new_type == "DISTRIBUTION":
            self.update_attribute(
                "groupType",
                (
                    self.get_attribute("groupType", False)
                    ^ pyadconstants.ADS_GROUP_TYPE["SECURITY_ENABLED"]
                ),
            )
        elif new_type == "SECURITY":
            self.update_attribute(
                "groupType",
                (
                    self.get_attribute("groupType", False)
                    ^ pyadconstants.ADS_GROUP_TYPE["SECURITY_ENABLED"]
                )
                | pyadconstants._ADS_GROUP_TYPE["SECURITY_ENABLED"],
            )
        else:
            raise ValueError("new_type", new_type, ("DISTRIBUTION", "SECURITY"))


ADObject._py_ad_object_mappings["group"] = ADGroup


def __get_memberOfs(self, recursive: bool = False, scope: str = "all") -> List[ADGroup]:
    """
    Returns a list of groups that the current object is a member of.

    :param recursive: This determines whether to return groups that the object is nested
        into indirectly, defaults to False
    :type recursive: bool, optional
    :param scope: Only return group membership within the current domain (queries from
        domain) (scope=domain), the forest (will only include universal groups, queries
        from global catalog) (scope=forest), or both (scope=all), defaults to "all"
    :type scope: str ["domain","forest","all"], optional
    :return: ADGroup
    :rtype: List[ADGroup]
    """

    return self._get_memberOfs(recursive, scope, [])


def __is_member_of(self, group: ADGroup, recursive=False) -> bool:
    """
    Check whether this object is a member of the given group

    :param group: The group to check if an object is a member of
    :type group: ADGroup
    :param recursive: This determines whether to return groups that the object is nested
        into indirectly, defaults to False
    :type recursive: bool, optional
    :return: True if the object is a member of the group, False otherwise
    :rtype: bool
    """

    return group in self.get_memberOfs(recursive=recursive)


def ___p_get_memberOfs(
    self, recursive: bool = False, scope: str = "all", processed_groups: list = []
) -> List[ADGroup]:
    """
    Returns a list of groups that the current object is a member of.

    :param recursive: This determines whether to return groups that the object is nested
        into indirectly, defaults to False
    :type recursive: bool, optional
    :param scope: Only return group membership within the current domain (queries from
        domain) (scope=domain), the forest (will only include universal groups, queries
        from global catalog) (scope=forest), or both (scope=all), defaults to "all"
    :type scope: str ["domain","forest","all"], optional
    :param processed_groups: reserved, leave empty, defaults to []
    :type processed_groups: list, optional
    :return: ADGroup
    :rtype: List[ADGroup]
    """

    if self not in processed_groups:
        if scope in ("domain", "all"):
            for dn in self.get_attribute("memberOf"):
                obj = ADGroup.from_dn(dn, options=self._make_options())
                if recursive and obj not in processed_groups and dn != self.dn:
                    new_members = obj._get_memberOfs(recursive, scope, processed_groups)
                    processed_groups.extend(new_members)
                processed_groups.append(obj)
        if scope in ("forest", "all"):
            for dn in self.get_attribute("memberOf", source="GC"):
                obj = ADGroup.from_dn(dn)
                if recursive and obj not in processed_groups and dn != self.dn:
                    new_members = obj._get_memberOfs(recursive, scope, processed_groups)
                    processed_groups.extend(new_members)
                processed_groups.append(obj)
    return list(set(processed_groups))


ADObject.get_memberOfs = __get_memberOfs
ADObject.is_member_of = __is_member_of
ADObject._get_memberOfs = ___p_get_memberOfs
