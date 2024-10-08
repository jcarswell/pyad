import logging
import sys
import win32com.client

from .pyadexceptions import SetupError

logger = logging.getLogger(__name__)
_adsi_provider = win32com.client.Dispatch("ADsNameSpaces")

try:
    # Discover default domain and forest information
    __default_domain_obj = _adsi_provider.GetObject("", "LDAP://rootDSE")
except:
    # If there was an error, this computer might not be on a domain.
    logger.info(
        "Unable to connect to default domain. "
        "Computer is likely not attached to an AD domain."
    )
    __default_domain_obj = None
    _default_detected_forest = None
    _default_detected_domain = None
else:
    # connecting to rootDSE will connect to the domain that the
    # current logged-in user belongs to.. which is generally the
    # domain under question and therefore becomes the default domain.
    _default_detected_forest = __default_domain_obj.Get("rootDomainNamingContext")
    _default_detected_domain = __default_domain_obj.Get("defaultNamingContext")


class ADBase(object):
    """
    Base class that is utilized by all objects within package to help
    store defaults. (search, query, all AD objects)
    """

    DEFAULTS_OPTIONS_MAPPINGS = [
        ("default_ldap_server", "server"),
        ("default_gc_server", "gc_server"),
        ("default_ldap_port", "port"),
        ("default_gc_port", "gc_port"),
        ("default_username", "username"),
        ("default_password", "password"),
        ("default_ldap_authentication_flag", "authentication_flag"),
        ("default_ssl", "ssl"),
    ]

    default_ssl = False
    default_ldap_server = None
    default_gc_server = None
    default_ldap_port = None
    default_gc_port = None
    default_username = None
    default_password = None
    default_ldap_protocol = "LDAP"
    default_ldap_authentication_flag = 0  # No credentials
    default_domain = _default_detected_domain
    default_forest = _default_detected_forest
    adsi_provider = _adsi_provider

    def _set_defaults(self, options):
        for (default, key) in ADBase.DEFAULTS_OPTIONS_MAPPINGS:
            if key in options:
                setattr(self, default, options[key])

    def _make_options(self):
        options = dict()
        for (default, key) in ADBase.DEFAULTS_OPTIONS_MAPPINGS:
            val = getattr(self, default)
            if val:
                options[key] = val
        return options

    @property
    def _safe_default_domain(self):
        if self.default_domain:
            return self.default_domain
        raise SetupError("Unable to detect default domain. Must specify search base.")

    @property
    def _safe_default_forest(self):
        if self.default_forest:
            return self.default_forest
        raise SetupError("Unable to detect default forest. Must specify search base.")


def set_defaults(**kwargs):
    for k, v in kwargs.items():
        setattr(ADBase, "_".join(("default", k)), v)
