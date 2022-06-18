from .adquery import ADQuery
from .adbase import ADBase


class SearchBase(ADQuery):
    base_dn = None

    def __init__(self, search_base: str = None, options: dict = None):
        super().__init__(options=options or {})
        if not search_base:
            if not ADBase.default_domain:
                raise Exception(
                    "Unable to detect default domain. Must specify search base."
                )
            self.base_dn = ADBase.default_domain

    def execute_query(self, **kwags) -> None:
        kwags.setdefault("base_dn", self.base_dn)
        return super().execute_query(**kwags)


def by_cn(cn: str, search_base: str = None, options: dict = None):
    searcher = SearchBase(search_base, options)
    searcher.execute_query(where_clause=("CN = '%s'" % cn), type="GC")

    if searcher.row_count > 0:
        return searcher.get_single_result()["distinguishedName"]
    else:
        return []


def by_upn(upn: str, search_base: str = None, options: dict = None):
    searcher = SearchBase(search_base, options)
    searcher.execute_query(where_clause=("userPrincipalName = '%s'" % upn), type="GC")

    if searcher.row_count > 0:
        return searcher.get_single_result()["distinguishedName"]
    else:
        return []


def by_sid(sid: str, search_base: str = None, options: dict = None):
    searcher = SearchBase(search_base, options)
    searcher.execute_query(where_clause=("objectSid = '%s'" % sid), type="GC")

    if searcher.row_count > 0:
        return searcher.get_single_result()["distinguishedName"]
    else:
        return []


def all_results_by_cn(cn: str, search_base: str = None, options: dict = None):
    searcher = SearchBase(search_base, options)
    searcher.execute_query(where_clause=("CN = '%s'" % cn), type="GC")
    if searcher.row_count > 0:
        return [result["distinguishedName"] for result in searcher.get_all_results()]
    else:
        return []


def all_results_by_upn(upn: str, search_base: str = None, options: dict = None):
    searcher = SearchBase(search_base, options)
    searcher.execute_query(where_clause=("userPrincipalName = '%s'" % upn), type="GC")
    if searcher.row_count > 0:
        return [result["distinguishedName"] for result in searcher.get_all_results()]
    else:
        return []


def all_results_by_sid(sid, search_base=None, options={}):
    searcher = SearchBase(search_base, options)
    searcher.execute_query(where_clause=("objectSid = '%s'" % sid), type="GC")
    if searcher.row_count > 0:
        return [result["distinguishedName"] for result in searcher.get_all_results()]
    else:
        return []
