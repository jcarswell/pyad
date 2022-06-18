import win32com

from warnings import warn
from typing import Iterator, List

from .adbase import ADBase
from . import pyadutils
from .pyadexceptions import noExecutedQuery


class ADQuery(ADBase):
    """
    ADQuery provides a search interface for active directory. Once initialized, a query
    can be executed by calling execute_query(). Once initialized and a query executed, the
    query object can be handled similarly to a File Handle object.

    To limit the result set when calling execute_query(), the base_dn, search_scope, and
    where_clause can be used.

    base_dn: The base distinguished name to search from. ie "CN=Users,DC=example,DC=com"
        will only return users from the CN=Users container.
        if unspecified, the default domain will be used ("DC=example,DC=com")

    search_scope: The scope of the search. Must be one of "subtree", "onelevel", or "base",

        - subtree: searches the entire subtree of the base_dn (default)

            If you are looking for users with a specific attribute value, using this will
            return all users with that attribute value that exist under the provided
            base_dn.
        - onelevel: searches the immediate children of the base_dn

            If you are looking for users with a specific attribute value, using this will
            return only users with that attribute value that exist directly under the
            current base_dn.
        - base: searches only the base_dn

            If you are looking for users with a specific attribute value, using this will
            only return a user if you specify that users distinguished name as the base_dn.

    where_clause: The filter to use when searching. ie "samaccountname='jdoe'" will only
        return distinguished names that have the samaccountname of jdoe.
        multiple filters can be combined using the AND or OR operator and prefixed with NOT.

        For example: "samaccountname='jdoe' OR samaccountname='jsmith' AND objectClass='person'"
        will return results that have the samaccountname of jdoe or jsmith and are a person.

    """

    # Requests secure authentication. When this flag is set,
    # Active Directory will use Kerberos, and possibly NTLM,
    # to authenticate the client.
    ADS_SECURE_AUTHENTICATION: int = 1
    # Requires ADSI to use encryption for data
    # exchange over the network.
    ADS_USE_ENCRYPTION: int = 2

    # ADS_SCOPEENUM enumeration. Documented at http://goo.gl/83G1S

    # Searches the whole subtree, including all the
    # children and the base object itself.
    ADS_SCOPE_SUBTREE: int = 2
    # Searches one level of the immediate children,
    # excluding the base object.
    ADS_SCOPE_ONELEVEL: int = 1
    # Limits the search to the base object.
    # The result contains, at most, one object.
    ADS_SCOPE_BASE: int = 0

    __queried: bool = False
    __position: int = 0
    __rs: "win32com.client.CDispatch" = None
    __rc: int = None

    # the methodology for performing a command with credentials
    # and for forcing encryption can be found at http://goo.gl/GGCK5

    def __init__(self, options: dict = {}) -> None:
        self.__adodb_conn = win32com.client.Dispatch("ADODB.Connection")
        if self.default_username and self.default_password:
            self.__adodb_conn.Provider = "ADsDSOObject"
            self.__adodb_conn.Properties("User ID").Value = self.default_username
            self.__adodb_conn.Properties("Password").Value = self.default_password
            adsi_flag = ADQuery.ADS_SECURE_AUTHENTICATION | ADQuery.ADS_USE_ENCRYPTION
            self.__adodb_conn.Properties("ADSI Flag").Value = adsi_flag
            self.__adodb_conn.Properties("Encrypt Password").Value = True
            self.__adodb_conn.Open()
        else:
            self.__adodb_conn.Open("Provider=ADSDSOObject")

    def reset(self) -> None:
        self.__rs = self.__rc = None
        self.__queried = False
        self.__position = None

    def execute_query(
        self,
        attributes: List[str] = ["distinguishedName"],
        where_clause: str = None,
        type: str = "LDAP",
        base_dn: str = None,
        page_size: int = 1000,
        search_scope: str = "subtree",
        options: dict = {},
        ldap_dialect: bool = False,
    ) -> None:
        """
        Query active directory with the given parameters. Once completed the class becomes
        iterable.

        :param attributes: A list of active directory attributes to query for each object
            in the resultant set, defaults to ["distinguishedName"]
        :type attributes: List[str], optional
        :param where_clause: Apply a filter when querying Active Directory, defaults to None
        :type where_clause: str, optional
        :param type: Whether the search should be a GC or LDAP query, defaults to "LDAP"
        :type type: str ["LDAP" or "GC"], optional
        :param base_dn: The search path, defaults to root distinguished name for the domain
        :type base_dn: str, optional
        :param page_size: maximum number of results to return, defaults to 1000
        :type page_size: int, optional
        :param search_scope: limit the depth of the search, defaults to "subtree"
        :type search_scope: str ["subtree", "onelevel", "base"], optional
        :param ldap_dialect: use the ldap dialect in the where_clause, defaults to False
        :type ldap_dialect: bool, optional
        :raises ValueError: if the search_scope is not one of "subtree", "onelevel", or "base"
        """

        assert type in ("LDAP", "GC")
        if not base_dn:
            if type == "LDAP":
                base_dn = self._safe_default_domain
            if type == "GC":
                base_dn = self._safe_default_forest
        # https://docs.microsoft.com/en-us/windows/win32/adsi/searching-with-activex-data-objects-ado

        # Ldap dialect
        if ldap_dialect:
            query = (
                f"<{pyadutils.generate_ads_path(base_dn, type, self.default_ldap_server, self.default_ldap_port)}"
                f">; {where_clause};{','.join(attributes)}"
            )
        else:
            # SQL dialect
            query = "SELECT %s FROM '%s'" % (
                ",".join(attributes),
                pyadutils.generate_ads_path(
                    base_dn, type, self.default_ldap_server, self.default_ldap_port
                ),
            )
            if where_clause:
                query = " ".join((query, "WHERE", where_clause))

        command = win32com.client.Dispatch("ADODB.Command")
        command.ActiveConnection = self.__adodb_conn
        command.Properties("Page Size").Value = page_size
        if search_scope in ["subtree", ADQuery.ADS_SCOPE_SUBTREE]:
            command.Properties("Searchscope").Value = ADQuery.ADS_SCOPE_SUBTREE
        elif search_scope in ["onelevel", ADQuery.ADS_SCOPE_ONELEVEL]:
            command.Properties("Searchscope").Value = ADQuery.ADS_SCOPE_ONELEVEL
        elif search_scope in ["base", ADQuery.ADS_SCOPE_BASE]:
            command.Properties("Searchscope").Value = ADQuery.ADS_SCOPE_BASE
        else:
            raise ValueError(
                "Unknown search_base %s, must be 'subtree', "
                "'onelevel' or 'base'" % search_scope
            )
        command.CommandText = query
        self.__rs, self.__rc = command.Execute()
        self.__queried = True

    def __len__(self) -> int:
        if not self.__queried:
            raise noExecutedQuery
        return self.__rs.RecordCount

    @property
    def row_count(self) -> int:
        return self.__rs.RecordCount

    def get_row_count(self):
        warn("User the len property instead", DeprecationWarning)
        return self.__rs.RecordCount

    def get_single_result(self) -> dict:
        """
        get_single_result Gets the next result in the result set.

        :raises noExecutedQuery: if called before calling execute_query()
        :return: values for the query result
        :rtype: dict
        """

        if not self.__queried:
            raise noExecutedQuery
        if self.row_count == 0:
            return {}
        # if not self.__rs.EOF and self.__position == 0:
        #    self.__rs.MoveFirst()
        #    self.__position = 1
        d = {}
        for f in self.__rs.Fields:
            d[f.Name] = f.Value

        self.__position += 1
        self.__rs.MoveNext()

        return d

    def get_results(self) -> None:
        """
        Iterator for the results of the query.

        :raises noExecutedQuery: If the query has not been executed yet.
        :yield: A dictionary of the requested attributes for the query result.
        :rtype: Iterator[dict]
        """

        if not self.__queried:
            raise noExecutedQuery
        if self.row_count == 0:
            yield {}
            return
        while not self.__rs.EOF:
            d = {}
            for f in self.__rs.Fields:
                d[f.Name] = f.Value
            yield d
            self.__position += 1
            self.__rs.MoveNext()

    def get_all_results(self) -> List[dict]:
        """
        returns all results of the query

        :raises noExecutedQuery: If the query has not been executed yet.
        :return: A list of dictionaries of the requested attributes for the query result.
        :rtype: list
        """

        if not self.__queried:
            raise noExecutedQuery
        l = []
        for d in self.get_results():
            l.append(d)
        return l

    def seek(self, pos: int) -> int:
        """
        Seek to a specific position in the result set.

        :param pos: the position to seek to
        :type pos: int
        :raises ValueError: if the position is out of range
        :return: the current position in the result set
        :rtype: int
        """

        if pos > self.row_count:
            raise ValueError("Cannot seek past end of result")
        self.__rs.MoveFirst()
        self.__position = 0
        while self.__position < pos:
            self.__rs.MoveNext()
            self.__position += 1

        return self.__position

    def tell(self) -> int:
        """
        Return the current position in the result set.

        :return: the current position in the result set
        :rtype: int
        """

        return self.__position

    def __iter__(self) -> Iterator[dict]:
        return self.get_results()

    def __next__(self) -> dict:
        return self.get_single_result()
