from .adobject import ADObject
from .pyadexceptions import InvalidObjectException, invalidResults


def from_cn(common_name, search_base=None, options={}) -> ADObject:
    """Generates ADObject based on common name"""
    Escape = {"\\": "\\5C", "*": "\\2A", "(": "\\28", ")": "\\29"}
    common_name = "".join([Escape.get(char, char) for char in common_name])
    try:
        q = ADObject.from_cn(common_name, search_base, options)
        q.adjust_pyad_type()
        return q
    except invalidResults:
        return None


def from_dn(distinguished_name, options={}) -> ADObject:
    """Generates ADObject based on distinguished name"""
    try:
        q = ADObject.from_dn(distinguished_name, options)
        q.adjust_pyad_type()
        return q
    except InvalidObjectException:
        return None


def from_guid(guid, options={}) -> ADObject:
    """Generates ADObject based on GUID"""
    try:
        q = ADObject.from_guid(guid, options)
        q.adjust_pyad_type()
        return q
    except InvalidObjectException:
        return None
