import unittest

from delphin.interfaces.ace import (InteractiveAce,)

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
            * Make result a tree and MRS object and compare
        """
        ace = TestInteractiveAce.ace
        self.assertEqual(ace.parse("I run"), {'RESULTS': [{'DERIV': '#T[1 "XP" nil 582 np_nb-frg_c #T[2 "N" nil 581 np-hdn_cpd_c #T[3 "NP" nil 578 hdn_bnp-pn_c #T[4 "N" "I" 64 i_pn_np1]] #T[5 "N" nil 580 hdn_optcmp_c #T[6 "N" nil 579 n_sg_ilr #T[7 "N" "run" 39 run_n1]]]]]', 'MRS': '#D[mrs TOP: <0>=#D[h] INDEX: <2>=#D[e SF: "prop-or-ques"] RELS: #D[*cons* FIRST: #D[unknown_rel LBL: <1>=#D[h] ARG0: <2>=#D[e SF: "prop-or-ques"] ARG: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"]] REST: #D[*cons* FIRST: #D[udef_q_rel LBL: <5>=#D[h] ARG0: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"] RSTR: <6>=#D[h] BODY: <7>=#D[h]] REST: #D[*cons* FIRST: #D[compound_rel LBL: <8>=#D[h] ARG0: <9>=#D[e SF: "prop" TENSE: "untensed" MOOD: "indicative" PROG: "-" PERF: "-"] ARG1: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"] ARG2: <10>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*cons* FIRST: #D[proper_q_rel LBL: <11>=#D[h] ARG0: <10>=#D[x PERS: "3" NUM: "pl" IND: "+"] RSTR: <12>=#D[h] BODY: <13>=#D[h]] REST: #D[*cons* FIRST: #D[named_rel LBL: <14>=#D[h] CARG: "\\"I\\"" ARG0: <10>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*cons* FIRST: #D["_run_n_of_rel" LBL: <8>=#D[h] ARG0: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"] ARG1: <16>=#D[i]] REST: #D[*null*] ] ] ] ] ] ] HCONS: #D[*cons* FIRST: #D[qeq HARG: <0>=#D[h] LARG: <1>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <6>=#D[h] LARG: <8>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <12>=#D[h] LARG: <14>=#D[h]] REST: #D[*null*] ] ] ]]'}], 'SENT': 'I run'})

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
