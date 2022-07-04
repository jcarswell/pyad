import pywintypes

from typing import Any, Dict, List
from .adobject import ADObject
from .aduser import ADUser
from .adcomputer import ADComputer
from .adgroup import ADGroup
from . import pyadconstants
from . import pyadutils


class ADContainer(ADObject):
    def get_children_iter(
        self, recursive: bool = False, filter: List[ADObject] = None
    ) -> ADObject:
        """
        Iterate over the children objects in the container.

        :param recursive: enumerate all containers with in the object,
            defaults to False
        :type recursive: bool, optional
        :param filter: filter to only specific object classes ie ADUser,
            defaults to None
        :type filter: List[ADObject], optional
        :yield: _description_
        :rtype: _type_
        """
        for com_object in self._ldap_adsi_obj:
            q = ADObject.from_com_object(com_object)
            q.adjust_pyad_type()
            if q.type == "organizationalUnit" and recursive:
                for c in q.get_children_iter(recursive=recursive):
                    if not filter or c.__class__ in filter:
                        yield c
            if not filter or q.__class__ in filter:
                yield q

    def get_children(
        self, recursive: bool = False, filter: List[ADObject] = None
    ) -> list:
        """
        returns a list of child containers with in the current container. Optionally
        the list can be filtered to specific object classes and search through child
        containers recursively.

        :param recursive: include children from sub-containers, defaults to False
        :type recursive: bool, optional
        :param filter: filter to only specific object classes ie ADUser, defaults to None
        :type filter: List[ADObject], optional
        :return: a list of all child objects
        :rtype: list
        """

        return list(self.get_children_iter(recursive=recursive, filter=filter))

    def __create_object(self, type_: str, name: str) -> ADObject:
        prefix = "ou" if type_ == "organizationalUnit" else "cn"
        prefixed_name = "=".join((prefix, name))
        return self._ldap_adsi_obj.Create(type_, prefixed_name)

    def create_user(
        self,
        name: str,
        password: str = None,
        upn_suffix: str = None,
        enable: bool = True,
        optional_attributes: dict = {},
    ) -> ADUser:
        """
        Create a new user object in the container.

        :param name: The name of the user
        :type name: str
        :param password: The password for the user it is strongly recommended to
            populate this parameter as the account will be created with password
            not required which will not get clear within AD leading to a security
            vulnerability.
        :type password: str, optional
        :param upn_suffix: The upn suffix for the user, defaults to default upn
            suffix for the domain.
        :type upn_suffix: str, optional
        :param enable: Whether the user should be enabled or disabled, defaults to True
        :type enable: bool, optional
        :param optional_attributes: List of additional attribute to set, defaults to {}
        :type optional_attributes: dict, optional
        :return: the created user object
        :rtype: ADUser
        """

        pyadobj = None

        try:
            if not upn_suffix:
                upn_suffix = self.get_domain().get_default_upn()
            upn = "@".join((name, upn_suffix))
            obj = self.__create_object("user", name)
            obj.Put("sAMAccountName", optional_attributes.get("sAMAccountName", name))
            obj.Put("userPrincipalName", upn)
            obj.SetInfo()
            pyadobj = ADUser.from_com_object(obj)

            if enable:
                pyadobj.enable()

            if password:
                pyadobj.set_password(password)
                pyadobj.set_user_account_control_setting("PASSWD_NOTREQD", False)

            pyadobj.set_user_account_control_setting("NORMAL_ACCOUNT", True)
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error as e:
            if pyadobj:
                # clean up the object if it was created
                pyadobj.delete()
            pyadutils.pass_up_com_exception(e)

    def create_group(
        self,
        name: str,
        security_enabled: bool = True,
        scope: str = "GLOBAL",
        optional_attributes: Dict[str, Any] = {},
    ) -> ADGroup:
        """
        Create a new group object in the container

        :param name: The Group Name
        :type name: str
        :param security_enabled: If this is a security enabled group or a distribution
            group, defaults to True
        :type security_enabled: bool, optional
        :param scope: The scope of group. Must be one of [GLOBAL, LOCAL, UNIVERSAL].
            Defaults to "GLOBAL"
        :type scope: str, optional
        :param optional_attributes: Additional attributes to set when creating the
            object, defaults to {}
        :type optional_attributes: Dict[str,Any], optional
        :return: The created group object
        :rtype: ADGroup
        """

        obj = None

        try:
            obj = self.__create_object("group", name)
            obj.Put("sAMAccountName", name)
            val = pyadconstants.ADS_GROUP_TYPE[scope]
            if security_enabled:
                val = val | pyadconstants.ADS_GROUP_TYPE["SECURITY_ENABLED"]
            obj.Put("groupType", val)
            obj.SetInfo()
            pyadobj = ADGroup.from_com_object(obj)
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error as e:
            if obj:
                obj.delete()
            pyadutils.pass_up_com_exception(e)
        except KeyError:
            if obj:
                obj.delete()
            raise ValueError(f"Invalid scope: {scope}")

    def create_container(
        self, name: str, optional_attributes: Dict[str, Any] = {}
    ) -> "ADContainer":
        """
        Create a new organizational unit in the container

        :param name: The name of the container
        :type name: str
        :param optional_attributes: Additional attributes to set when creating the
            object, defaults to {}
        :type optional_attributes: Dict[str,Any], optional
        :return: the created container object
        :rtype: ADContainer
        """

        obj = None

        try:
            obj = self.__create_object("organizationalUnit", name)
            obj.SetInfo()
            pyadobj = ADContainer.from_com_object(obj)
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error as e:
            if obj:
                obj.delete()
            pyadutils.pass_up_com_exception(e)

    def create_computer(
        self, name: str, enable: bool = True, optional_attributes: Dict[str, Any] = {}
    ) -> ADComputer:
        """
        Create a new computer object in the container

        :param name: The computer name
        :type name: str
        :param enable: Whether the computer should be enabled or disabled,
            defaults to True
        :type enable: bool, optional
        :param optional_attributes: Additional attributes to set when creating the
            object, defaults to {}
        :type optional_attributes: Dict[str,Any], optional
        :return: the created computer object
        :rtype: ADComputer
        """

        obj = None

        try:
            obj = self.__create_object("computer", name)
            obj.Put("sAMAccountName", name + "$")
            if enable:
                obj.Put("userAccountControl", 4128)
            else:
                obj.Put("userAccountControl", 4130)
            obj.SetInfo()
            pyadobj = ADComputer.from_com_object(obj)
            if enable:
                pyadobj.enable()
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error as e:
            if obj:
                obj.delete()
            pyadutils.pass_up_com_exception(e)

    def remove_child(self, child: ADObject) -> None:
        """Removes the child object from the domain"""

        self._ldap_adsi_obj.Delete(child.type, child.prefixed_cn)


ADObject._py_ad_object_mappings["organizationalUnit"] = ADContainer
ADObject._py_ad_object_mappings["container"] = ADContainer
