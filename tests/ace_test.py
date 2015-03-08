import unittest

from delphin.interfaces.ace import InteractiveAce
from delphin.derivation import Derivation

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
        """
        ace = TestInteractiveAce.ace
        text = "I run"
        result = ace.parse(text)
        self.assertEqual(result['SENT'], text)
        self.assertEqual(len(result['RESULTS']), 1)
        self.assertEqual(Derivation(result['RESULTS'][0]), Derivation('#T[1 "XP" nil 582 np_nb-frg_c #T[2 "N" nil 581 np-hdn_cpd_c #T[3 "NP" nil 578 hdn_bnp-pn_c #T[4 "N" "I" 64 i_pn_np1]] #T[5 "N" nil 580 hdn_optcmp_c #T[6 "N" nil 579 n_sg_ilr #T[7 "N" "run" 39 run_n1]]]]]'))


    def test_request_mrs(self):
        """
        TODO:
            * Use simplemrs.py to compare Mrs
        """
        ace = TestInteractiveAce.ace
        text = "I run"
        result = ace.parse(text)
        self.assertEqual(result['SENT'], text)
        self.assertEqual(len(result['RESULTS']), 1)
        self.assertEqual(Derivation(result['RESULTS'][0]), Derivation('#T[1 "XP" nil 582 np_nb-frg_c #T[2 "N" nil 581 np-hdn_cpd_c #T[3 "NP" nil 578 hdn_bnp-pn_c #T[4 "N" "I" 64 i_pn_np1]] #T[5 "N" nil 580 hdn_optcmp_c #T[6 "N" nil 579 n_sg_ilr #T[7 "N" "run" 39 run_n1]]]]]'))


    def test_request_avm(self):
        ace = TestInteractiveAce.ace
        text = "I run"
        result = ace.parse(text)
        self.assertEqual(result['SENT'], text)
        self.assertEqual(len(result['RESULTS']), 1)
        self.assertEqual(Derivation(result['RESULTS'][0]), Derivation('#T[1 "XP" nil 582 np_nb-frg_c #T[2 "N" nil 581 np-hdn_cpd_c #T[3 "NP" nil 578 hdn_bnp-pn_c #T[4 "N" "I" 64 i_pn_np1]] #T[5 "N" nil 580 hdn_optcmp_c #T[6 "N" nil 579 n_sg_ilr #T[7 "N" "run" 39 run_n1]]]]]'))


    def test_parse_punctuation(self):
        ace = TestInteractiveAce.ace
        text = "Don't go"
        result = ace.parse(text)
        self.assertEqual(result['SENT'], text)
        self.assertEqual(len(result['RESULTS']), 1)
        self.assertEqual(Derivation(result['RESULTS'][0]), Derivation('#T[20 "XP" nil 569 vp_fin-frg_c #T[21 "VP" nil 568 hd-cmp_u_c #T[22 "V" "don’t" 81 do1_neg_4_u] #T[23 "VP" nil 567 hd_optcmp_c #T[24 "V" nil 566 v_n3s-bse_ilr #T[25 "V" "go" 38 go_v1]]]]]'))

    def test_parse_empty(self): 
        ace = TestInteractiveAce.ace
        self.assertEqual(ace.parse(""), {'SENT': '', 'RESULTS': []})
       
    def test_parse_negative(self):
        ace = TestInteractiveAce.ace
        sent = "Je suis heureux"
        self.assertEqual(ace.parse(sent), {'SENT': sent, 'RESULTS': []})

    def test_parse_consistent(self):
        ace = TestInteractiveAce.ace
        sent = "I run."
        gold = ace.parse(sent)
        gold_derivations = [Derivation(parse) for parse in gold['RESULTS']]
        for i in range(10):
            result = ace.parse(sent)
            self.assertEqual(result['SENT'], sent)
            self.assertEqual(result['SENT'], gold['SENT'])
            for i, parse in enumerate(result['RESULTS']):
                self.assertEqual(Derivation(parse), gold_derivations[i])

    @unittest.skip
    def test_send_parse(self):
        self.assertTrue(False)

    @unittest.skip
    def test_receive_parse(self):
        self.assertTrue(False)

    
class FakePexpect(object):
        
    def __init__(self):
        pass
