from __future__ import absolute_import
from .pyadunittest import ADTestCase
from pyad.adbase import ADBase
import pyad

class TestADBase(ADTestCase):
    def setUp(self):
        # set all defaults back to their default
        ADBase.default_ldap_server = None
        ADBase.default_gc_server = None
        ADBase.default_ldap_port = None
        ADBase.default_gc_port = None
    
    def test_detected_forest(self):
        self.assertEqual(ADBase.default_domain, self.SANDBOX_DOMAIN)
    
    def test_detected_domain(self):
        self.assertEqual(ADBase.default_forest, self.SANDBOX_FOREST)
    
    def test_set_defaults(self):
        pyad.set_defaults(ldap_server = self.TEST_DC, ldap_port = 389)
        self.assertEqual(ADBase.default_ldap_server, self.TEST_DC)
        self.assertEqual(ADBase.default_ldap_port, 389)
