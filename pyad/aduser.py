from .adobject import ADObject
import pywintypes
from . import pyadutils
import datetime


class ADUser(ADObject):
    @classmethod
    def create(
        cls,
        name,
        container_object,
        password=None,
        upn_suffix=None,
        enable=True,
        optional_attributes={},
    ):
        """Creates and returns a new active directory user"""
        return container_object.create_user(
            name=name,
            password=password,
            upn_suffix=upn_suffix,
            enable=enable,
            optional_attributes=optional_attributes,
        )

    def set_password(self, password, flush=True):
        """Sets the users password"""
        try:
            self._ldap_adsi_obj.SetPassword(password)
            if flush:
                self._flush()
        except pywintypes.com_error as excpt:
            pyadutils.pass_up_com_exception(excpt)

    def force_pwd_change_on_login(self, flush: bool = True):
        """Forces the user to change their password the next time they login"""
        self.update_attribute("PwdLastSet", 0, no_flush=(not flush))

    def grant_password_lease(self, flush: bool = True):
        self.update_attribute("PwdLastSet", -1, no_flush=(not flush))

    def get_password_last_set(self) -> datetime.datetime:
        """Returns datetime object of when user last reset their password."""
        return self._get_password_last_set()

    def get_max_pwd_age(self):
        """Returns timespan object representing the max password age on a user's domain"""
        return pyadutils.convert_timespan(self.get_domain().maxPwdAge)

    def get_expiration(self):
        """Gets the expiration date of the password as a datetime object.
        The _ldap_adsi_obj.AccountExpirationDate can be inaccurate and
        return the UNIX Epoch instead of the true expiration date."""
        uac_settings = self.get_user_account_control_settings()
        if any(
            uac_settings[flag]
            for flag in [
                "SMARTCARD_REQUIRED",
                "DONT_EXPIRE_PASSWD",
                "WORKSTATION_TRUST_ACCOUNT",
                "SERVER_TRUST_ACCOUNT",
                "INTERDOMAIN_TRUST_ACCOUNT",
            ]
        ):
            return None
        elif self.get_attribute("pwdLastSet", False) is None:
            return datetime.datetime(1970, 1, 1)
        else:
            return self.get_password_last_set() + self.get_max_pwd_age()

    def set_expiration(self, dt, flush: bool = True) -> None:
        """Sets the expiration date of the password to the given value"""
        self._ldap_adsi_obj.AccountExpirationDate = dt
        if flush:
            self._flush()

    def get_password_expired(self) -> bool:
        """Returns a bool representing whether the password has expired.
        The passwordexpired property will often return True even if not expired."""
        expiration_date = self.get_expiration()
        if expiration_date is None:
            return False
        return expiration_date < datetime.datetime.now()

    def unlock(self, flush: bool = True) -> None:
        """Unlock the user's account"""
        self.update_attribute("lockoutTime", 0, no_flush=(not flush))

    def set_managedby(self, user, flush: bool = True) -> None:
        """Sets managedBy on object to the specified user"""
        if not isinstance(user, ADUser):
            raise ValueError(f"Expected AD User object got {type(user)}")
        if user:
            self.update_attribute("manager", user.dn, no_flush=(not flush))
        else:
            self.clear_managedby("manager", flush=flush)

    def clear_managedby(self, flush: bool = True) -> None:
        """Sets object to be managedBy nobody"""
        self.clear_attribute("manager", flush=flush)


ADObject._py_ad_object_mappings["user"] = ADUser
