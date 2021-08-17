import unittest
import pyad

class ADTestCase(unittest.TestCase):
    SANDBOX_OU = "ou=testing,dc=example,dc=com"
    SANDBOX_DOMAIN = "dc=example,dc=com"
    SANDBOX_FOREST = "dc=example,dc=com"
    
    TEST_DC = 'dc01'
    
    KNOWN_EXISTS_USER = 'testuset'
    KNOWN_EXISTS_COMPUTER = 'testcomputer'
    KNOWN_DNE_OBJECT = "testdne"

    def assertHasAttribute(self, obj, attribute):
        self.assertTrue(hasattr(obj._ldap_adsi_obj, attribute))
        
    def assertAttributeValue(self, obj, attribute, value):
        self.assertEqual(obj._ldap_adsi_obj.GetEx(attribute), value)