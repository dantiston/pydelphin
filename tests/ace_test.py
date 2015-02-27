import unittest

from delphin.interfaces.ace import InteractiveAce
from delphin.derivations.derivationtree import Derivation

class TestAceParser(unittest.TestCase):

    def setUp(self):
        pass


class TestAceGenerator(unittest.TestCase):

    def setUp(self):
        pass
    

class TestInteractiveAce(unittest.TestCase):            

    @classmethod
    def setUpClass(self):
        # TODO: Find the ERG
        TestInteractiveAce.ace = InteractiveAce('/home/dantiston/delphin/erg.dat')
        TestInteractiveAce.fake = FakePexpect()

    @classmethod
    def tearDownClass(self):
        TestInteractiveAce.ace.close()

    def test_pass(self):
        TestInteractiveAce.ace._pass

    def test_open(self):
        """
        __init__() calls _open(), so assume everything is running after setup
        """
        from pexpect import spawnu

        ace = TestInteractiveAce.ace
        self.assertEqual(ace._p.__class__, spawnu)
        self.assertEqual(ace._p.expect(""), 0) # Output should be empty

    def test_parse(self):
        """
        TODO: 
            * Move result to external json file
            * Make a comparable MRS object and compare
        """
        ace = TestInteractiveAce.ace
        self.assertEqual(ace.parse("I run"), {'RESULTS': [Derivation('#T[1 "XP" nil 582 np_nb-frg_c #T[2 "N" nil 581 np-hdn_cpd_c #T[3 "NP" nil 578 hdn_bnp-pn_c #T[4 "N" "I" 64 i_pn_np1]] #T[5 "N" nil 580 hdn_optcmp_c #T[6 "N" nil 579 n_sg_ilr #T[7 "N" "run" 39 run_n1]]]]]')], 'SENT': 'I run'})

    def test_parse_empty(self): 
        ace = TestInteractiveAce.ace
        self.assertEqual(ace.parse(""), {'SENT': '', 'RESULTS': []})
       
    def test_parse_negative(self):
        ace = TestInteractiveAce.ace
        sent = "Je suis heureux"
        self.assertEqual(ace.parse(sent), {'SENT': sent, 'RESULTS': []})

    def test_parse_consistent(self):
        """
        Each parse increments an internal ACE counter,
            so need to use a more robust comparison than strings
        """
        ace = TestInteractiveAce.ace
        sent = "I run."
        result = ace.parse(sent)
        for i in range(10):
            self.assertEqual(ace.parse(sent), result)

    def test_send_parse(self):
        self.assertTrue(False)

    def test_receive_parse(self):
        self.assertTrue(False)

    
class FakePexpect(object):
        
    def __init__(self):
        pass
