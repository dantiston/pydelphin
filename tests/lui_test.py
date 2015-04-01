import unittest

import re

from delphin.interfaces import lui
from delphin.interfaces.ace import InteractiveAce

# For testing equality
from delphin.derivation import Derivation
from delphin.mrs.xmrs import Mrs
from delphin.mrs.compare import isomorphic

# For testing mrs/avm
from delphin.mrs.components import MrsVariable, HandleConstraint, ElementaryPredication, Pred, Argument, Hook


class TestLui(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # TODO: Change path to a standardized path
        cls.parser = InteractiveAce("~/delphin/erg.dat")
        cls.text = "I run"

        cls.gold_mrs_string = """avm 20 #D[mrs TOP: <0>=#D[h] INDEX: <2>=#D[e SF: "prop" TENSE: "pres" MOOD: "indicative" PROG: "-" PERF: "-"] RELS: #D[*cons* FIRST: #D[pron_rel LBL: <4>=#D[h] ARG0: <3>=#D[x PERS: "1" NUM: "sg" PRONTYPE: "std_pron"]] REST: #D[*cons* FIRST: #D[pronoun_q_rel LBL: <5>=#D[h] ARG0: <3>=#D[x PERS: "1" NUM: "sg" PRONTYPE: "std_pron"] RSTR: <6>=#D[h] BODY: <7>=#D[h]] REST: #D[*cons* FIRST: #D["_like_v_1_rel" LBL: <1>=#D[h] ARG0: <2>=#D[e SF: "prop" TENSE: "pres" MOOD: "indicative" PROG: "-" PERF: "-"] ARG1: <3>=#D[x PERS: "1" NUM: "sg" PRONTYPE: "std_pron"] ARG2: <8>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*cons* FIRST: #D[udef_q_rel LBL: <9>=#D[h] ARG0: <8>=#D[x PERS: "3" NUM: "pl" IND: "+"] RSTR: <10>=#D[h] BODY: <11>=#D[h]] REST: #D[*cons* FIRST: #D["_dog_n_1_rel" LBL: <12>=#D[h] ARG0: <8>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*null*] ] ] ] ] ] HCONS: #D[*cons* FIRST: #D[qeq HARG: <0>=#D[h] LARG: <1>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <6>=#D[h] LARG: <4>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <10>=#D[h] LARG: <12>=#D[h]] REST: #D[*null*] ] ] ]] "Simple MRS\""""
        cls.gold_mrs_tokens = ['avm', '20', '#D', '[', 'mrs', 'TOP', ':', '<', '0', '>', '=', '#D', '[', 'h', ']', 'INDEX', ':', '<', '2', '>', '=', '#D', '[', 'e', 'SF', ':', '"prop"', 'TENSE', ':', '"pres"', 'MOOD', ':', '"indicative"', 'PROG', ':', '"-"', 'PERF', ':', '"-"', ']', 'RELS', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'pron_rel', 'LBL', ':', '<', '4', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'pronoun_q_rel', 'LBL', ':', '<', '5', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', 'RSTR', ':', '<', '6', '>', '=', '#D', '[', 'h', ']', 'BODY', ':', '<', '7', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', '"_like_v_1_rel"', 'LBL', ':', '<', '1', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '2', '>', '=', '#D', '[', 'e', 'SF', ':', '"prop"', 'TENSE', ':', '"pres"', 'MOOD', ':', '"indicative"', 'PROG', ':', '"-"', 'PERF', ':', '"-"', ']', 'ARG1', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', 'ARG2', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'udef_q_rel', 'LBL', ':', '<', '9', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', 'RSTR', ':', '<', '10', '>', '=', '#D', '[', 'h', ']', 'BODY', ':', '<', '11', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', '"_dog_n_1_rel"', 'LBL', ':', '<', '12', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', ']', 'REST', ':', '#D', '[', '*null*', ']', ']', ']', ']', ']', ']', 'HCONS', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '0', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '1', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '6', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '4', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '10', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '12', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*null*', ']', ']', ']', ']', ']', '"Simple MRS"']
        cls.gold_mrs_mapping = {
            "TOP":{'value':
                       ['[', 'h', ']'], 
                   'id': '0'},

            "INDEX":{'value':
                         ['[', 'e', 'SF', ':', '"prop"', 'TENSE', ':', '"pres"', 'MOOD', ':', '"indicative"', 'PROG', ':', '"-"', 'PERF', ':', '"-"', ']'],
                     'id': '2'},

            "RELS":{'value':
                        ['[', '*cons*', 'FIRST', ':', '#D', '[', 'pron_rel', 'LBL', ':', '<', '4', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'pronoun_q_rel', 'LBL', ':', '<', '5', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', 'RSTR', ':', '<', '6', '>', '=', '#D', '[', 'h', ']', 'BODY', ':', '<', '7', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', '"_like_v_1_rel"', 'LBL', ':', '<', '1', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '2', '>', '=', '#D', '[', 'e', 'SF', ':', '"prop"', 'TENSE', ':', '"pres"', 'MOOD', ':', '"indicative"', 'PROG', ':', '"-"', 'PERF', ':', '"-"', ']', 'ARG1', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', 'ARG2', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'udef_q_rel', 'LBL', ':', '<', '9', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', 'RSTR', ':', '<', '10', '>', '=', '#D', '[', 'h', ']', 'BODY', ':', '<', '11', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', '"_dog_n_1_rel"', 'LBL', ':', '<', '12', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', ']', 'REST', ':', '#D', '[', '*null*', ']', ']', ']', ']', ']', ']']},

            "HCONS":{'value':
                         ['[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '0', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '1', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '6', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '4', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '10', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '12', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*null*', ']', ']', ']', ']']},
        }

        # Build gold MRS
        ## Handles
        handles = [MrsVariable(vid=i, sort='h') for i in range(0,13)]
        ## Top
        top = MrsVariable(vid=0, sort='h')
        ## Arguments
        ### Pronoun x argument
        pron_arg_properties = {
            "PERS":"1",
            "NUM":"sg",
            "PRONTYPE":"std_pron",
        }
        pron_arg = MrsVariable(vid=3, sort="x", properties=pron_arg_properties)
        ### Like e argument
        like_arg_properties = {
            "SF":"prop",
            "TENSE":"pres",
            "MOOD":"indicative",
            "PROG":"-",
            "PERF":"-",
        }
        like_arg = MrsVariable(vid=2, sort="e", properties=like_arg_properties)
        ### Dogs x argument
        dogs_arg_properties = {
            "PERS":"3",
            "NUM":"pl",
            "IND":"+",
        }
        dogs_arg = MrsVariable(vid=8, sort="x", properties=dogs_arg_properties)
        ## RELS
        cls.rels = (
            # "I" relation
            ElementaryPredication(
                Pred.stringpred('pron_rel'),
                label=MrsVariable(vid=4, sort="h"),
                args=(Argument.mrs_argument('ARG0', pron_arg),)
            ),
            # PRON_Q relation
            ElementaryPredication(
                Pred.stringpred('pronoun_q_rel'),
                label=MrsVariable(vid=5, sort="h"),
                args=(Argument.mrs_argument('ARG0', pron_arg),
                      Argument.mrs_argument('RSTR', handles[6]),
                      Argument.mrs_argument('BODY', handles[7]))
            ),
            # "like" relation
            ElementaryPredication(
                Pred.stringpred('"_like_v_1_rel"'),
                label=MrsVariable(vid=1, sort="h"),
                args=(Argument.mrs_argument('ARG0', like_arg),
                      Argument.mrs_argument('ARG1', pron_arg),
                      Argument.mrs_argument('ARG2', dogs_arg),)
            ),
            # "dogs" relation
            ElementaryPredication(
                Pred.stringpred('"_dog_n_1_rel"'),
                label=MrsVariable(vid=12, sort="h"),
                args=(Argument.mrs_argument('ARG0', dogs_arg),)
            ),
            # UDEF_Q relation
            ElementaryPredication(
                Pred.stringpred('udef_q_rel'),
                label=MrsVariable(vid=9, sort="h"),
                args=(Argument.mrs_argument('ARG0', dogs_arg),
                      Argument.mrs_argument('RSTR', handles[10]),
                      Argument.mrs_argument('BODY', handles[11]))
            ),
        )
        ## HCONS
        cls.hcons = (
            HandleConstraint.qeq(handles[0], handles[1]),
            HandleConstraint.qeq(handles[6], handles[4]),
            HandleConstraint.qeq(handles[10], handles[12]),
        )
        ## HOOK
        cls.hook = Hook(top=top, index=like_arg)
        # Build gold Mrs
        cls.goldMrs = Mrs(hook=cls.hook,
                          rels=cls.rels,
                          hcons=cls.hcons)


    def setUp(self):
        self.parser = InteractiveAce("~/delphin/erg.dat")
        self.text = "I run"


    # Basic tests
    def testParse(self):
        """
        TODO: 
            * Move result to external json file
        """
        result = lui.parse(__class__.parser, __class__.text)
        self.assertEqual(result['SENT'], __class__.text)
        self.assertEqual(len(result['RESULTS']), 1)
        self.assertEqual(Derivation(result['RESULTS'][0]), Derivation('#T[1 "XP" nil 582 np_nb-frg_c #T[2 "N" nil 581 np-hdn_cpd_c #T[3 "NP" nil 578 hdn_bnp-pn_c #T[4 "N" "I" 64 i_pn_np1]] #T[5 "N" nil 580 hdn_optcmp_c #T[6 "N" nil 579 n_sg_ilr #T[7 "N" "run" 39 run_n1]]]]]'))


    @unittest.skip
    def testGenerate(self):
        self.fail("Need to implement Generate()!")


    # Request tests
    def testRequestParse(self):
        lui.request_parse(__class__.parser, __class__.text)
        expectation = [re.compile(r"parse .*?\r\n")]
        self.assertEqual(__class__.parser._p.expect(expectation), 0)


    def testRequestMRS(self):
        datum = "I like dogs."
        # Request / process parse
        lui.request_parse(self.parser, datum)
        lui.receive_derivations(self.parser, datum)
        # Request MRS
        lui.request_mrs(self.parser, 1, 1)
        expectation = [re.compile(r"avm .*?\r\n")]
        self.assertEqual(self.parser._p.expect(expectation), 0)


    @unittest.skip
    def testRequestAVM(self):
        self.parser._p.sendline("parse I like dogs.\f")
        lui.request_avm(self.parser, 1, 1)
        expectation = [re.compile(r"avm .*?\r\n")]
        self.assertEqual(self.parser._p.expect(expectation), 0)


    @unittest.skip
    def testRequestGenerate(self):
        self.fail("Need to implement Generate()!")


    @unittest.skip
    def testRequestUnify(self):
        self.fail("Need to implement Unify()!")


    # Receive tests
    def testReceiveDerivations(self):
        target = "I like dogs."
        __class__.parser._p.sendline("parse %s" % target)
        response = lui.receive_derivations(__class__.parser, target)
        self.assertEqual(response['SENT'], target)
        self.assertEqual(len(response['RESULTS']), 2)


    def testReceiveMRS(self):
        datum = "I like dogs."
        # Request / process parse
        lui.request_parse(self.parser, datum)
        lui.receive_derivations(self.parser, datum)
        # Request MRS
        lui.request_mrs(self.parser, 1, 1)
        # Receive MRS
        response = lui.receive_mrs(self.parser)
        tag = response.split(None, 1)[0]
        sort = response.rsplit('"', 2)[-2]
        self.assertEqual(tag, "avm")
        self.assertEqual(sort, "Simple MRS")


    def testReceiveAVM(self):
        pass


    def testReceiveSentences(self):
        pass


    # Load tests
    def testLoadDerivationsList(self):
        result = lui.load_derivations("""tree 1 #T[1 "S" nil 843 sb-hd_mc_c #T[2 "NP" nil 837 hdn_bnp-qnt_c #T[3 "NP" "I" 85 i]] #T[4 "VP" nil 842 hd-cmp_u_c #T[5 "V" nil 838 v_n3s-bse_ilr #T[6 "V" "like" 56 like_v1]] #T[7 "NP" nil 841 hdn_bnp_c #T[8 "N" nil 840 w_period_plr #T[9 "N" nil 839 n_pl_olr #T[10 "N" "dogs." 62 dog_n1]]]]]] "I like dogs."

tree 1 #T[11 "XP" nil 836 np_frg_c #T[12 "NP" nil 835 hdn_bnp_c #T[13 "N" nil 834 aj-hdn_norm_c #T[14 "AP" nil 831 sp-hd_hc_c #T[15 "N" "I" 83 i_pn_np1] #T[16 "AP" "like" 61 like_a1]] #T[17 "N" nil 833 w_period_plr #T[18 "N" nil 832 n_pl_olr #T[19 "N" "dogs." 62 dog_n1]]]]]] "I like dogs.\"""")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(tree, Derivation) for tree in result))
        # TODO: Test the trees against stored json


    def testLoadDerivations(self):
        result = lui.load_derivations("""tree 1 #T[1 "S" nil 843 sb-hd_mc_c #T[2 "NP" nil 837 hdn_bnp-qnt_c #T[3 "NP" "I" 85 i]] #T[4 "VP" nil 842 hd-cmp_u_c #T[5 "V" nil 838 v_n3s-bse_ilr #T[6 "V" "like" 56 like_v1]] #T[7 "NP" nil 841 hdn_bnp_c #T[8 "N" nil 840 w_period_plr #T[9 "N" nil 839 n_pl_olr #T[10 "N" "dogs." 62 dog_n1]]]]]] "I like dogs.\"""")
        self.assertEqual(len(result), 1)
        self.assertTrue(all(isinstance(tree, Derivation) for tree in result))
        # TODO: Test the trees against stored json


    ## AVM Tests
    def testLoadAVM(self):
        pass


    ## MRS Tests
    def testLoadMrs(self):
        # MRS for "I like dogs." from ERG 1212
        result = lui.load_mrs(__class__.gold_mrs_string)
        self.assertTrue(isomorphic(__class__.goldMrs, result))


    # Dump tests
    def testDumpTree(self):
        pass


    def testDumpAVM(self):
        pass


    def testDumpMRS(self):
        pass
