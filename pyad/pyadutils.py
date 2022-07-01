import datetime
import win32api
import win32security
import pywintypes

from .adbase import ADBase
from .pyadconstants import GENERIC_ADSI_ERRORS, GENERIC_COM_ERRORS, WIN32_ERRORS
from .pyadexceptions import genericADSIException, comException, win32Exception


def validate_credentials(
    username: str, password: str, domain: str = None
) -> "win32.PyHandle":
    """
    validate_credentials
    Validates credentials; returns a PyHANDLE object with a bool value
    of True if the credentials are valid, else returns None.
    Note that if the user would not be able to log on; for example,
    due to the account being expired; None will be returned.

    :param username: username
    :type username: str
    :param password: password
    :type password: str
    :param domain: domain name, defaults to None
    :type domain: str, optional
    :return: PyHandle Object with a bool of true. or None
    :rtype: win32.PyHandle
    """
    try:
        valid = win32security.LogonUser(
            username,
            domain,
            password,
            win32security.LOGON32_LOGON_NETWORK,
            win32security.LOGON32_PROVIDER_DEFAULT,
        )
        assert valid, "Valid should ALWAYS have a true value"
        return valid
    except pywintypes.error:
        return None


def convert_error_code(error_code: int) -> int:
    """
    Convert error code from the format returned by pywin32 to the format that Microsoft
    documents everything in.

    :param error_code: error code
    :type error_code: int
    :return: The error code in the format Microsoft documents it
    :rtype: int
    """

    return error_code % 2**32


def interpret_com_exception(
    excp: "pywintype.com_error", additional_info: dict = {}
) -> dict:
    """
    Convert a pywin32 com_error exception into a dictionary of error information.

    :param excp: pywin32 com_error exception
    :type excp: pywintype.com_error
    :param additional_info: any additional information with the error, defaults to {}
    :type additional_info: dict, optional
    :return: a dictionary of error information
    :rtype: dict
    """

    d = {}
    d["error_num"] = convert_error_code(excp.args[2][5])
    # for some reason hex() includes the L for long in the hex...
    # however since it's a string, we don't care...
    # since L would never be in a hex code, we can safely just remove it.
    d["error_code"] = hex(d["error_num"]).rstrip("L")
    if d["error_code"][0:7] == "0x80005":
        if d["error_num"] in list(GENERIC_ADSI_ERRORS.keys()):
            d["exception_type"] = "known_generic_adsi_error"
            d["error_constant"] = GENERIC_ADSI_ERRORS[d["error_num"]][0]
            d["message"] = " ".join(GENERIC_ADSI_ERRORS[d["error_num"]][1:3])
        else:
            # this supposedly should not happen, but I'd rather be ready for
            # the case that Microsoft made a typo somewhere than die weirdly.
            d["error_constant"] = None
            d["exception_type"] = "unknown_generic_adsi_error"
            d["message"] = "unknown generic ADSI error"
            d["exception"] = genericADSIException
    elif d["error_code"][0:6] == "0x8007":
        d["exception_type"] = "win32_error"
        d["error_constant"] = None
        # returns information about error from winerror.h file...
        d["message"] = win32api.FormatMessage(d["error_num"])
    elif d["error_num"] in list(GENERIC_COM_ERRORS.keys()):
        d["exception_type"] = "generic_com_error"
        d["error_constant"] = GENERIC_COM_ERRORS[d["error_num"]][0]
        d["message"] = GENERIC_COM_ERRORS[d["error_num"]][1]
    else:
        d["exception_type"] = "unknown"
        d["error_constant"] = None
        d["message"] = excp.args[2][4]
    d["additional_info"] = additional_info = {}
    return d


def pass_up_com_exception(excp: "pywintype.com_error", additional_info: dict = {}):
    """
    reparse the com_error into a sane exception and raise it.

    :param excp: the com_error exception
    :type excp: pywintype.com_error
    :param additional_info: Additional exception details, defaults to {}
    :type additional_info: dict, optional
    :raises excp: if we don't know how to handle the exception raise the original
        exception
    """

    if excp.__class__ in (genericADSIException, comException, win32Exception):
        raise excp
    else:
        info = interpret_com_exception(excp)
        type_ = info["exception_type"]
        if type_ == "win32_error":
            # raise exception defined in WIN32_ERRORs if there is one...
            # otherwise, just raise a generic win32Exception
            raise WIN32_ERRORS.get(info["error_num"], win32Exception)(
                error_info=info, additional_info=additional_info
            )
        elif type_ == "known_generic_adsi_error":
            raise GENERIC_ADSI_ERRORS[info["error_num"]][3](
                error_info=info, additional_info=additional_info
            )
        elif type_ == "unknown_generic_adsi_error":
            raise genericADSIException(error_info=info, additional_info=additional_info)
        else:
            raise comException(error_info=info, additional_info=additional_info)


def convert_datetime(adsi_time_com_obj):
    """
    Converts 64-bit integer COM object representing time into
    a python datetime object.

    Credit goes to John Nielsen who documented this at
    `<http://docs.activestate.com/activepython/2.6/pywin32/html/com/help/active_directory.html>`_.
    """

    if not hasattr(adsi_time_com_obj, "highpart") or not hasattr(
        adsi_time_com_obj, "lowpart"
    ):
        raise ValueError(
            f"Expected adsi_time object got '{adsi_time_com_obj.__class__.__name__}'"
        )
    high_part = int(adsi_time_com_obj.highpart) << 32
    low_part = int(adsi_time_com_obj.lowpart)
    date_value = ((high_part + low_part) - 116444736000000000) // 10000000
    #
    # The "fromtimestamp" function in datetime cannot take a
    # negative value, so if the resulting date value is negative,
    # explicitly set it to 18000. This will result in the date
    # 1970-01-01 00:00:00 being returned from this function
    #
    if date_value < 0:
        date_value = 18000
    return datetime.datetime.fromtimestamp(date_value)


def convert_bigint(obj) -> int:
    """
    Converts a ADSI time object to an integer.

    based on http://www.selfadsi.org/ads-attributes/user-usnChanged.htm

    :param obj: the AD bigint object
    :raises AttributeError: invalid object type
    :return: the decimal value of the object
    :rtype: int
    """

    if hasattr(obj, "HighPart") and hasattr(obj, "LowPart"):
        h, l = obj.HighPart, obj.LowPart
        if l < 0:
            h += 1
        return (h << 32) + l
    else:
        raise AttributeError(
            f"Expected adsi time object got '{obj.__class__.__name__}'"
        )


def convert_timespan(obj) -> datetime.timedelta:
    """
    Converts COM object representing time span to a python time span object.

    :param obj: ADSI time span object
    :return: the python timedelta object
    :rtype: datetime.timedelta
    """

    as_seconds = (
        abs(convert_bigint(obj)) / 10000000
    )  # number of 100 nanoseconds in a second
    return datetime.timedelta(seconds=as_seconds)


def convert_guid(guid_object):
    return pywintypes.IID(guid_object, True)


def convert_sid(sid_object):
    return pywintypes.SID(bytes(sid_object))


def generate_list(input) -> list:
    """
    converts a set or tuple to a list or returns the input in a list if it is not
    a list.

    :param input: a list like object or any
    :type input: list, set, tuple, Any
    :return: a list
    :rtype: list
    """

    if type(input) is list:
        return input
    elif type(input) in (set, tuple):
        return list(input)
    else:
        return [
            input,
        ]


def escape_path(path: str) -> str:
    """
    escapes a path for use in ADSI.

    :param path: the raw path to escape
    :type path: str
    :return: the escaped path
    :rtype: str
    """

    escapes = (
        ("\+", "+"),
        ("\*", "*"),
        ("\(", "("),
        ("\)", ")"),
        ("\/", "/"),
        ("\\,", ",,"),
        ("\\", "\\5c"),
        ("*", "\\2a"),
        ("(", "\\28"),
        (")", "\\29"),
        ("/", "\\2f"),
        ("+", "\\2b"),
        (chr(0), "\\00"),
    )
    for char, escape in escapes:
        path = path.replace(char, escape)
    path = path.replace(",,", "\\2c")
    return path


def generate_ads_path(
    distinguished_name: str, type: str, server: str = None, port: int = None
) -> str:
    """
    Generates a proper ADsPath to be used when connecting to an active directory object or
    when searching active directory.

    :param distinguished_name: DN of object or search base such as
        'cn=John Smith,cn=users,dc=example,dc=com'
    :type distinguished_name: str
    :param type: the connection type, either 'LDAP', 'LDAPS', or 'GC'
    :type type: str
    :param server: FQDN of domain controller if necessary to connect to a particular server,
        defaults to the global catalog server
    :type server: str, optional
    :param port: port number for directory service if not default port.
        If port is specified, server must be specified.
    :type port: int, optional
    :raises TypeError: Invalid type for type
    :return: the ADsPath to be used when connecting to Active Directory
    :rtype: str
    """

    if type == "LDAP" or type == "LDAPS":
        server = server if server else ADBase.default_ldap_server
        port = port if port else ADBase.default_ldap_port
    elif type == "GC":
        server = server if server else ADBase.default_gc_server
        port = port if port else ADBase.default_gc_port
    else:
        raise TypeError("Invalid type specified.")

    ads_path = "".join((type, "://"))
    if server:
        ads_path = "".join((ads_path, server))
        if port:
            ads_path = ":".join((ads_path, str(port)))
        ads_path = "".join((ads_path, "/"))
    ads_path = "".join((ads_path, escape_path(distinguished_name)))
    return ads_path
