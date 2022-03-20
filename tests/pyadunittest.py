import unittest
from .config import TestConfiguration

class ADTestCase(unittest.TestCase,TestConfiguration):
    def assertHasAttribute(self, obj, attribute):
        self.assertTrue(hasattr(obj._ldap_adsi_obj, attribute))
        
    def assertAttributeValue(self, obj, attribute, value):
        self.assertEqual(obj._ldap_adsi_obj.GetEx(attribute), value)