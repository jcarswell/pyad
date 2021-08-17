from __future__ import absolute_import
from .adbase import *
from . import pyadutils

class ADQuery(ADBase):
    # Requests secure authentication. When this flag is set,
    # Active Directory will use Kerberos, and possibly NTLM,
    # to authenticate the client.
    ADS_SECURE_AUTHENTICATION = 1
    # Requires ADSI to use encryption for data
    # exchange over the network.
    ADS_USE_ENCRYPTION = 2

    # ADS_SCOPEENUM enumeration. Documented at http://goo.gl/83G1S

    # Searches the whole subtree, including all the
    # children and the base object itself.
    ADS_SCOPE_SUBTREE = 2
    # Searches one level of the immediate children,
    # excluding the base object.
    ADS_SCOPE_ONELEVEL = 1
    # Limits the search to the base object.
    # The result contains, at most, one object.
    ADS_SCOPE_BASE = 0

    # the methodology for performing a command with credentials
    # and for forcing encryption can be found at http://goo.gl/GGCK5

    def __init__(self, options:dict ={}) -> None:
        self.__adodb_conn = win32com.client.Dispatch("ADODB.Connection")
        if self.default_username and self.default_password:
            self.__adodb_conn.Provider = u"ADsDSOObject"
            self.__adodb_conn.Properties("User ID").Value = self.default_username
            self.__adodb_conn.Properties("Password").Value = self.default_password
            adsi_flag = ADQuery.ADS_SECURE_AUTHENTICATION | \
                            ADQuery.ADS_USE_ENCRYPTION
            self.__adodb_conn.Properties("ADSI Flag").Value = adsi_flag
            self.__adodb_conn.Properties("Encrypt Password").Value = True
            self.__adodb_conn.Open("Provider=ADSDSOObject")
        else:
            self.__adodb_conn.Open("Provider=ADSDSOObject")

        self.reset()

    def reset(self) -> None:
        self.__rs = self.__rc = None
        self.__queried = False
        self.__position = 0

    def execute_query(self, attributes:list[str] =["distinguishedName"], where_clause:str =None,
                    type:str ="LDAP", base_dn:str =None, page_size:int =1000, search_scope:str ="subtree",
                    options:dict ={}, ldap_dialect:bool =False) -> None:
        assert type in ("LDAP", "GC")
        if not base_dn:
            if type == "LDAP":
                base_dn = self._safe_default_domain
            if type == "GC":
                base_dn = self._safe_default_forest
        # https://docs.microsoft.com/en-us/windows/win32/adsi/searching-with-activex-data-objects-ado

        # Ldap dialect
        if ldap_dialect:
            query = f"<{pyadutils.generate_ads_path(base_dn, type, self.default_ldap_server, self.default_ldap_port)}>; {where_clause};{','.join(attributes)}"
        else:
        # SQL dialect
            query = "SELECT %s FROM '%s'" % (','.join(attributes),
                    pyadutils.generate_ads_path(base_dn, type,
                            self.default_ldap_server, self.default_ldap_port))
            if where_clause:
                query = ' '.join((query, 'WHERE', where_clause))

        command = win32com.client.Dispatch("ADODB.Command")
        command.ActiveConnection = self.__adodb_conn
        command.Properties("Page Size").Value = page_size
        if search_scope == "subtree":
            command.Properties("Searchscope").Value = ADQuery.ADS_SCOPE_SUBTREE
        elif search_scope == "onelevel":
            command.Properties("Searchscope").Value = ADQuery.ADS_SCOPE_ONELEVEL
        elif search_scope == "base":
            command.Properties("Searchscope").Value = ADQuery.ADS_SCOPE_BASE
        else:
            raise Exception("Unknown search_base %s, must be subtree, "\
                            "onelevel or base" % search_scope)
        command.CommandText = query
        self.__rs, self.__rc = command.Execute()
        self.__queried = True

    @property
    def row_count(self) -> int:
        return self.__rs.RecordCount

    def get_row_count(self):
        DeprecationWarning("User the row_count property instead")
        return self.__rs.RecordCount

    def get_single_result(self) -> dict:
        """
        Gets the next result in the result set.

        Raises:
            noExecutedQuery: if called before calling execute_query()

        Returns:
            dict: a dictionary contining the values for the query result
        """

        if not self.__queried:
            raise noExecutedQuery
        if not self.__rs.EOF and self.__position == 0:
            self.__rs.MoveFirst()
            self.__position = 1
        d = {}
        for f in self.__rs.Fields:
            d[f.Name] = f.Value

        self.__position += 1
        self.__rs.MoveNext()

        return d

    def get_results(self) -> list[dict]:
        if not self.__queried:
            raise noExecutedQuery
        if not self.__rs.EOF:
            self.__rs.MoveFirst()
            self.__position = 1
        while not self.__rs.EOF:
            d = {}
            for f in self.__rs.Fields:
                d[f.Name] = f.Value
            yield d
            self.__position += 1
            self.__rs.MoveNext()

    def get_all_results(self) -> list:
        if not self.__queried:
            raise noExecutedQuery
        l = []
        for d in self.get_results():
            l.append(d)
        return l

    def seek(self,pos:int) -> int:
        if pos > self.row_count:
            raise ValueError("Cannot seek past end of result")
        self.__rs.MoveFirst()
        self.__position = 1
        for x in len(pos):
            self.MoveNext()
            self.__position += 1
            if self.__position == pos:
                break
        
        return self.__position

    def tell(self) -> int:
        return self.__position