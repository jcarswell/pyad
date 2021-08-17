
__all__ = ["set_defaults","ADQuery","ADComputer","ADContainer","ADDomain","ADGroup",
           "ADUser","from_cn","from_dn","from_guid","comException",
           "genericADSIException","win32Exception","invalidOwnerException",
           "noObjectFoundException","InvalidObjectException","InvalidAttribute",
           "noExecutedQuery","invalidResults"]

def _check_requirments():
    import sys
    import importlib
    required_version = (3, 6)
    cont = True
    msg = "Please ensure the following packages are installed:"
    if sys.version_info < required_version:
        raise ImportError("Requires at least Python 3.6")
    for x in ['win32api','pywintypes','win32com','win32security']:
        try:
            importlib.import_module(x)
        except ModuleNotFoundError:
            cont = False
            msg = f"{msg} {x}"
    if not cont:
        raise ImportError(msg)
_check_requirments()

from .adbase import set_defaults
from .adquery import ADQuery
from .adcomputer import ADComputer
from .adcontainer import ADContainer
from .addomain import ADDomain
from .adgroup import ADGroup
from .aduser import  ADUser
from .pyad import from_cn,from_dn,from_guid
from .pyadexceptions import (comException,genericADSIException,win32Exception,
                             invalidOwnerException,noObjectFoundException,
                             InvalidObjectException,InvalidAttribute,
                             noExecutedQuery,invalidResults)