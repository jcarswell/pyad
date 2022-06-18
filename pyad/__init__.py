__all__ = [
    "set_defaults",
    "ADQuery",
    "ADComputer",
    "ADContainer",
    "ADDomain",
    "ADGroup",
    "ADUser",
    "from_cn",
    "from_dn",
    "from_guid",
    "comException",
    "genericADSIException",
    "win32Exception",
    "invalidOwnerException",
    "noObjectFoundException",
    "InvalidObjectException",
    "InvalidAttribute",
    "noExecutedQuery",
    "invalidResults",
]


def _check_requirements():
    import sys
    import importlib

    required_version = (3, 6)
    cont = True
    msg = []
    if sys.version_info < required_version:
        raise ImportError("Requires at least Python 3.6")
    if sys.platform != "win32":
        raise Exception("Must be running Windows in order to use pyad.")
    for x in ["win32api", "pywintypes", "win32com", "win32security"]:
        try:
            importlib.import_module(x)
        except ModuleNotFoundError:
            cont = False
            msg.append(f"{x}")
    if not cont:
        raise ImportError(
            "Please ensure the following packages are installed: " + ", ".join(msg)
        )


_check_requirements()

from .adbase import set_defaults
from .adquery import ADQuery
from .adcomputer import ADComputer
from .adcontainer import ADContainer
from .addomain import ADDomain
from .adgroup import ADGroup
from .aduser import ADUser
from .pyad import from_cn, from_dn, from_guid
from .pyadexceptions import (
    comException,
    genericADSIException,
    win32Exception,
    invalidOwnerException,
    noObjectFoundException,
    InvalidObjectException,
    InvalidAttribute,
    noExecutedQuery,
    invalidResults,
)
