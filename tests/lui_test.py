import unittest

import re

from delphin.interfaces import lui
from delphin.interfaces.ace import InteractiveAce

# For testing equality
from delphin.derivation import Derivation
from delphin.mrs.xmrs import Mrs
from delphin.mrs.compare import isomorphic
from delphin.mrs import simplemrs

# For testing mrs/avm
from delphin.mrs.components import MrsVariable, HandleConstraint, ElementaryPredication, Pred, Argument, Hook
from delphin.tfs import TypedFeatureStructure
from delphin.tdl import tokenize


class TestLui(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # TODO: Change path to a standardized path
        cls.parser = InteractiveAce("~/delphin/erg.dat")
        cls.text = "I run"
        cls.goldText = "I like dogs."

        # MRS for "I like dogs." from ERG
        cls.gold_mrs_string = """avm 20 #D[mrs TOP: <0>=#D[h] INDEX: <2>=#D[e SF: "prop" TENSE: "pres" MOOD: "indicative" PROG: "-" PERF: "-"] RELS: #D[*cons* FIRST: #D[pron_rel LBL: <4>=#D[h] ARG0: <3>=#D[x PERS: "1" NUM: "sg" PRONTYPE: "std_pron"]] REST: #D[*cons* FIRST: #D[pronoun_q_rel LBL: <5>=#D[h] ARG0: <3>=#D[x PERS: "1" NUM: "sg" PRONTYPE: "std_pron"] RSTR: <6>=#D[h] BODY: <7>=#D[h]] REST: #D[*cons* FIRST: #D["_like_v_1_rel" LBL: <1>=#D[h] ARG0: <2>=#D[e SF: "prop" TENSE: "pres" MOOD: "indicative" PROG: "-" PERF: "-"] ARG1: <3>=#D[x PERS: "1" NUM: "sg" PRONTYPE: "std_pron"] ARG2: <8>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*cons* FIRST: #D[udef_q_rel LBL: <9>=#D[h] ARG0: <8>=#D[x PERS: "3" NUM: "pl" IND: "+"] RSTR: <10>=#D[h] BODY: <11>=#D[h]] REST: #D[*cons* FIRST: #D["_dog_n_1_rel" LBL: <12>=#D[h] ARG0: <8>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*null*] ] ] ] ] ] HCONS: #D[*cons* FIRST: #D[qeq HARG: <0>=#D[h] LARG: <1>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <6>=#D[h] LARG: <4>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <10>=#D[h] LARG: <12>=#D[h]] REST: #D[*null*] ] ] ]] "Simple MRS\"^L"""
        #cls.gold_mrs_tokens = ['avm', '20', '#D', '[', 'mrs', 'TOP', ':', '<', '0', '>', '=', '#D', '[', 'h', ']', 'INDEX', ':', '<', '2', '>', '=', '#D', '[', 'e', 'SF', ':', '"prop"', 'TENSE', ':', '"pres"', 'MOOD', ':', '"indicative"', 'PROG', ':', '"-"', 'PERF', ':', '"-"', ']', 'RELS', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'pron_rel', 'LBL', ':', '<', '4', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'pronoun_q_rel', 'LBL', ':', '<', '5', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', 'RSTR', ':', '<', '6', '>', '=', '#D', '[', 'h', ']', 'BODY', ':', '<', '7', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', '"_like_v_1_rel"', 'LBL', ':', '<', '1', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '2', '>', '=', '#D', '[', 'e', 'SF', ':', '"prop"', 'TENSE', ':', '"pres"', 'MOOD', ':', '"indicative"', 'PROG', ':', '"-"', 'PERF', ':', '"-"', ']', 'ARG1', ':', '<', '3', '>', '=', '#D', '[', 'x', 'PERS', ':', '"1"', 'NUM', ':', '"sg"', 'PRONTYPE', ':', '"std_pron"', ']', 'ARG2', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'udef_q_rel', 'LBL', ':', '<', '9', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', 'RSTR', ':', '<', '10', '>', '=', '#D', '[', 'h', ']', 'BODY', ':', '<', '11', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', '"_dog_n_1_rel"', 'LBL', ':', '<', '12', '>', '=', '#D', '[', 'h', ']', 'ARG0', ':', '<', '8', '>', '=', '#D', '[', 'x', 'PERS', ':', '"3"', 'NUM', ':', '"pl"', 'IND', ':', '"+"', ']', ']', 'REST', ':', '#D', '[', '*null*', ']', ']', ']', ']', ']', ']', 'HCONS', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '0', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '1', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '6', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '4', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*cons*', 'FIRST', ':', '#D', '[', 'qeq', 'HARG', ':', '<', '10', '>', '=', '#D', '[', 'h', ']', 'LARG', ':', '<', '12', '>', '=', '#D', '[', 'h', ']', ']', 'REST', ':', '#D', '[', '*null*', ']', ']', ']', ']', ']', '"Simple MRS"']
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

        cls.other_mrs_string = '''avm 8 #D[mrs TOP: <0>=#D[h] INDEX: <2>=#D[e SF: "prop-or-ques"] RELS: #D[*cons* FIRST: #D[unknown_rel LBL: <1>=#D[h] ARG0: <2>=#D[e SF: "prop-or-ques"] ARG: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"]] REST: #D[*cons* FIRST: #D[udef_q_rel LBL: <5>=#D[h] ARG0: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"] RSTR: <6>=#D[h] BODY: <7>=#D[h]] REST: #D[*cons* FIRST: #D[compound_rel LBL: <8>=#D[h] ARG0: <9>=#D[e SF: "prop" TENSE: "untensed" MOOD: "indicative" PROG: "-" PERF: "-"] ARG1: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"] ARG2: <10>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*cons* FIRST: #D[proper_q_rel LBL: <11>=#D[h] ARG0: <10>=#D[x PERS: "3" NUM: "pl" IND: "+"] RSTR: <12>=#D[h] BODY: <13>=#D[h]] REST: #D[*cons* FIRST: #D[named_rel LBL: <14>=#D[h] CARG: "\\"I\\"" ARG0: <10>=#D[x PERS: "3" NUM: "pl" IND: "+"]] REST: #D[*cons* FIRST: #D["_run_n_of_rel" LBL: <8>=#D[h] ARG0: <4>=#D[x PERS: "3" NUM: "sg" IND: "+"] ARG1: <16>=#D[i]] REST: #D[*null*] ] ] ] ] ] ] HCONS: #D[*cons* FIRST: #D[qeq HARG: <0>=#D[h] LARG: <1>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <6>=#D[h] LARG: <8>=#D[h]] REST: #D[*cons* FIRST: #D[qeq HARG: <12>=#D[h] LARG: <14>=#D[h]] REST: #D[*null*] ] ] ]] "Simple MRS"\x0c\r\n'''

        cls.third_mrs_string = '''[ TOP: h0 INDEX: e2 [e  SF: prop TENSE: pres MOOD: indicative PROG: - PERF: -] RELS: < [pron_rel LBL: h4 ARG0: x3 [x  PERS: 1 NUM: sg PRONTYPE: std_pron]]  [pronoun_q_rel LBL: h5 ARG0: x3 [x  PERS: 1 NUM: sg PRONTYPE: std_pron] RSTR: h6 BODY: h7]  ["_think_v_1_rel" LBL: h1 ARG0: e2 [e  SF: prop TENSE: pres MOOD: indicative PROG: - PERF: -] ARG1: x3 [x  PERS: 1 NUM: sg PRONTYPE: std_pron] ARG2: h8 ARG3: i9]  [udef_q_rel LBL: h10 ARG0: x11 [x  PERS: 3 NUM: pl IND: +] RSTR: h12 BODY: h13]  [card_rel LBL: h14 CARG: \"3\" ARG0: e16 [e  SF: prop TENSE: untensed MOOD: indicative] ARG1: x11 [x  PERS: 3 NUM: pl IND: +]]  ["_zebra_n_1_rel" LBL: h14 ARG0: x11 [x  PERS: 3 NUM: pl IND: +]]  ["_fly_v_to_rel" LBL: h17 ARG0: e18 [e  SF: prop TENSE: past MOOD: indicative PROG: - PERF: -] ARG1: x11 [x  PERS: 3 NUM: pl IND: +] ARG2: x19 [x  PERS: 3 NUM: pl IND: +]]  [udef_q_rel LBL: h20 ARG0: x19 [x  PERS: 3 NUM: pl IND: +] RSTR: h21 BODY: h22]  ["_zeppelin_n_1_rel" LBL: h23 ARG0: x19 [x  PERS: 3 NUM: pl IND: +]]  [_over_p_rel LBL: h23 ARG0: e24 [e  SF: prop TENSE: untensed MOOD: indicative] ARG1: x19 [x  PERS: 3 NUM: pl IND: +] ARG2: x25 [x  PERS: 3 NUM: sg IND: +]]  [proper_q_rel LBL: h26 ARG0: x25 [x  PERS: 3 NUM: sg IND: +] RSTR: h27 BODY: h28]  [named_rel LBL: h29 CARG: \"Zimbabwe\" ARG0: x25 [x  PERS: 3 NUM: sg IND: +]] > HCONS: <  h0 qeq h1  h6 qeq h4  h8 qeq h17  h12 qeq h14  h21 qeq h23  h27 qeq h29  > ]'''

        ### AVM
        #### Build test AVM

        ##### SYNSEM
        ###### LOCAL
        ####### CAT
        ######## HEAD
        ctype_avm = TypedFeatureStructure(type="ctype", coref=14,
                                          featvals={"-CTYPE-":TypedFeatureStructure(type="string")})
        altmin_avm = TypedFeatureStructure(type="quant_rel", coref=13)
        min_avm = TypedFeatureStructure(type="norm_nom_rel", coref=12)
        minors_avm = TypedFeatureStructure(type="minors", featvals={"MIN": min_avm, "ALTMIN": altmin_avm})
        noun_avm = TypedFeatureStructure(type="noun", featvals={"MINORS": minors_avm,
                                                                "--CTYPE":ctype_avm,
                                                                "POSS":TypedFeatureStructure(type="-"),
                                                                "--BARE":TypedFeatureStructure(type="bool"),
                                                                "PRD":TypedFeatureStructure(type="bool"),
                                                                "CASE":TypedFeatureStructure(type="case"),
                                                                "AUX":TypedFeatureStructure(type="luk"),
                                                                "--HID":TypedFeatureStructure(coref=15, type="string"),
                                                                "MOD":TypedFeatureStructure(type="*null*")})

        ######## VAL
        ######### SPR
        ########## NON_LOCALx
        spr_non_local_que_avm = TypedFeatureStructure(type="*diff-list*",
                                                      coref=20,
                                                      featvals={"LAST":TypedFeatureStructure(type="*list*"),
                                                                "LIST":TypedFeatureStructure(type="*list*")})
        spr_non_local_rel_avm = TypedFeatureStructure(type="0-1-dlist",
                                                      coref=19,
                                                      featvals={"LAST":TypedFeatureStructure(type="*list*"),
                                                                "LIST":TypedFeatureStructure(type="0-1-list")})
        spr_non_local_slash_avm = TypedFeatureStructure(type="0-1-dlist",
                                                        coref=18,
                                                        featvals={"LAST":TypedFeatureStructure(type="*list*"),
                                                                  "LIST":TypedFeatureStructure(type="*locallist*")})
        spr_non_local_avm = TypedFeatureStructure(type="non-local", featvals={"QUE":spr_non_local_que_avm,
                                                                              "REL":spr_non_local_rel_avm,
                                                                              "SLASH":spr_non_local_slash_avm})
        ########## LOCAL
        spr_ctype_avm = TypedFeatureStructure(type="ctype",
                                              featvals={"-CTYPE-":TypedFeatureStructure(type="string")})
        spr_minors_avm = TypedFeatureStructure(type="minors_basic",
                                               featvals={"MIN":TypedFeatureStructure(type="predsort")})
        spr_head_avm = TypedFeatureStructure(type="det", featvals={"POSS":TypedFeatureStructure(type="bool"),
                                                                   "--BARE":TypedFeatureStructure(type="bool"),
                                                                   "PRD":TypedFeatureStructure(type="bool"),
                                                                   "CASE":TypedFeatureStructure(type="case"),
                                                                   "AUX":TypedFeatureStructure(type="luk"),
                                                                   "--HID":TypedFeatureStructure(type="string"),
                                                                   "MOD":TypedFeatureStructure(type="*list*"),
                                                                   "--CTYPE":spr_ctype_avm,
                                                                   "MINORS":spr_minors_avm})
        spr_val_avm = TypedFeatureStructure(type="valence", featvals={"COMPS":TypedFeatureStructure(type="*list*"),
                                                                      "SPR":TypedFeatureStructure(type="*olist*"),
                                                                      "SUBJ":TypedFeatureStructure(type="*null*")})
        spr_cat_avm = TypedFeatureStructure(type="cat_min1", featvals={"VAL":spr_val_avm, "HEAD":spr_head_avm})
        spr_local_avm = TypedFeatureStructure(type="local_min1", featvals={"CAT":spr_cat_avm})
        
        spr_synsem_avm = TypedFeatureStructure(type="synsem",
                                               coref=17,
                                               featvals={"MODIFD":TypedFeatureStructure(type="xmod_min"),
                                                         "LEX":TypedFeatureStructure(type="+"),
                                                         "PHON":TypedFeatureStructure(type="phon_min"),
                                                         "--SIND":TypedFeatureStructure(type="*top*"),
                                                         "OPT":TypedFeatureStructure(type="-"),
                                                         "PUNCT":TypedFeatureStructure(type="punctuation_min"),
                                                         "NONLOC":spr_non_local_avm,
                                                         "--MIN":TypedFeatureStructure(coref=13),
                                                         "LOCAL":spr_local_avm})

        spr_avm = TypedFeatureStructure(type="*cons*", featvals={"FIRST":spr_synsem_avm, 
                                                                 "REST":TypedFeatureStructure(type="*null*")})

        ######### SPEC
        spec_anti_synsem_avm = TypedFeatureStructure(type="anti_synsem_min",
                                                     featvals={"NONLOC":TypedFeatureStructure(type="non-local_min"),
                                                               "LOCAL":TypedFeatureStructure(type="mod_local")})
        spec_avm = TypedFeatureStructure(type="*cons*", featvals={"FIRST":spec_anti_synsem_avm,
                                                                  "REST":TypedFeatureStructure(type="*null*")})


        valence_avm = TypedFeatureStructure(type="valence_sp", featvals={"SUBJ":TypedFeatureStructure(type="*null*"),
                                                                         "SPCMPS":TypedFeatureStructure(type="*null*"),
                                                                         "COMPS": TypedFeatureStructure(coref=16, type="*null*"),
                                                                         "SPEC": spec_avm,
                                                                         "SPR": spr_avm})


        cat_avm = TypedFeatureStructure(type="cat", featvals={"HEAD":noun_avm,
                                                              "VAL":valence_avm,
                                                              "POSTHD":TypedFeatureStructure(type="bool"),
                                                              "MC":TypedFeatureStructure(type="na"),
                                                              "NEGPOL":TypedFeatureStructure(type="luk"),
                                                              "HS-LEX":TypedFeatureStructure(type="-"),
                                                              "HC-LEX":TypedFeatureStructure(type="-")})

        ####### CONT
        ######## HOOK
        xarg_avm = TypedFeatureStructure(type="*top*")
        sltop_avm = TypedFeatureStructure(type="handle", featvals={"SORT":TypedFeatureStructure(type="*sort*"),
                                                                   "INSTLOC":TypedFeatureStructure(type="string")})
        ltop_avm = TypedFeatureStructure(coref=8)
        index_avm = TypedFeatureStructure(coref=9)
        hook_avm = TypedFeatureStructure(type="hook", featvals={"XARG":xarg_avm,
                                                                "--SLTOP":sltop_avm,
                                                                "LTOP":ltop_avm,
                                                                "INDEX":index_avm})
        ######## HCONS
        hcons_avm = TypedFeatureStructure(type="*diff-list*", featvals={"LIST":TypedFeatureStructure(coref=11, type="*list*"),
                                                                        "LAST":TypedFeatureStructure(coref=11)})
        ######### RELS
        png_avm = TypedFeatureStructure(type="png", featvals={"PN":TypedFeatureStructure(type="pn"),
                                                              "GEN":TypedFeatureStructure(type="real_gender")})
        rels_nom_arg0_avm = TypedFeatureStructure(type="ref-ind",
                                                  coref=9,
                                                  featvals={"SORT":TypedFeatureStructure(type="entity"),
                                                            "IND":TypedFeatureStructure(type="+"),
                                                            "INSTLOC":TypedFeatureStructure(type="string"),
                                                            "DIV":TypedFeatureStructure(type="bool"),
                                                            "--TPC":TypedFeatureStructure(type="luk"),
                                                            "PNG":png_avm})
        rels_nom_lbl_avm = TypedFeatureStructure(type="handle", coref=8, featvals={"SORT":TypedFeatureStructure(type="*sort*"),
                                                                                   "INSTLOC":TypedFeatureStructure(type="string")})
        rels_nom_rel_avm = TypedFeatureStructure(type="reg_nom_relation",
                                                 coref=7,
                                                 featvals={"LNK":TypedFeatureStructure(type="*list*"),
                                                           "PRED":TypedFeatureStructure(type='"_dog_n_1_rel"'),
                                                           "CTO":TypedFeatureStructure(coref=3),
                                                           "CFROM":TypedFeatureStructure(coref=2),
                                                           "ARG0":rels_nom_arg0_avm,
                                                           "LBL":rels_nom_lbl_avm})
        rels_list_rest_avm = TypedFeatureStructure(type="*list*", coref=10)
        rels_list_avm = TypedFeatureStructure(type="*cons*", featvals={"FIRST":rels_nom_rel_avm, "REST":rels_list_rest_avm})
        rels_avm = TypedFeatureStructure(type="*diff-list*", featvals={"LIST":rels_list_avm,
                                                                       "LAST":TypedFeatureStructure(coref=10)})

        cont_avm = TypedFeatureStructure(type="nom-obj", featvals={"HOOK":hook_avm, "HCONS":hcons_avm, "RELS":rels_avm})
        
        ####### OTHERS
        agr_avm = TypedFeatureStructure(coref=9)
        arg_s_avm = TypedFeatureStructure(type="*cons*", featvals={"FIRST":TypedFeatureStructure(coref=17),
                                                                   "REST":TypedFeatureStructure(coref=16)})

        local_avm = TypedFeatureStructure(type="local", featvals={"CAT":cat_avm,
                                                                  "CONT":cont_avm,
                                                                  "AGR":agr_avm,
                                                                  "ARG-S":arg_s_avm,
                                                                  "CONJ":TypedFeatureStructure(type="cnil"),
                                                                  "CTXT":TypedFeatureStructure(type="ctxt_min")})

        ###### NONLOC
        non_local_rel_avm = TypedFeatureStructure(coref=19)
        non_local_slash_avm = TypedFeatureStructure(coref=18)
        non_local_que_avm = TypedFeatureStructure(coref=20)
        non_local_avm = TypedFeatureStructure(type="non-local", featvals={"REL":non_local_rel_avm, 
                                                                          "SLASH":non_local_slash_avm, 
                                                                          "QUE":non_local_que_avm})

        ###### MODIFD
        modified_avm = TypedFeatureStructure(type="notmod", featvals={"LPERIPH":TypedFeatureStructure(type="luk"),
                                                                      "RPERIPH":TypedFeatureStructure(type="luk")})

        ###### PHON
        tnt_main_avm = TypedFeatureStructure(type="tnt_main", featvals={"+PRB":TypedFeatureStructure(type='"1.0"'),
                                                                        "+TAG":TypedFeatureStructure(type='"NNS"')})
        tnt_avm = TypedFeatureStructure(type="null_tnt", featvals={"+PRBS":TypedFeatureStructure(type="*null*"),
                                                                   "+TAGS":TypedFeatureStructure(type="*null*"),
                                                                   "+MAIN":tnt_main_avm})
        id_avm = TypedFeatureStructure(type="*diff-list*", featvals={"LIST":TypedFeatureStructure(type="*list*"),
                                                                     "LAST":TypedFeatureStructure(type="*list*")})
        token_head_avm = TypedFeatureStructure(type="token_head", featvals={"+LL":TypedFeatureStructure(coref=14),
                                                                            "+TG":TypedFeatureStructure(coref=15)})
        trait_avm = TypedFeatureStructure(type="token_trait", featvals={"+IT":TypedFeatureStructure(type="italics"),
                                                                        "+UW":TypedFeatureStructure(type="-"),
                                                                        "+LB":TypedFeatureStructure(coref=4),
                                                                        "+RB":TypedFeatureStructure(coref=5),
                                                                        "+HD":token_head_avm})
        token_avm = TypedFeatureStructure(type="token",
                                          coref=22,
                                          featvals={"+CARG":TypedFeatureStructure(type='"dogs"'),
                                                    "+TICK":TypedFeatureStructure(type="bool"),
                                                    "+PRED":TypedFeatureStructure(type="predsort"),
                                                    "+TO":TypedFeatureStructure(coref=3),
                                                    "+FROM":TypedFeatureStructure(coref=2),
                                                    "+FORM":TypedFeatureStructure(coref=1),
                                                    "+CLASS":TypedFeatureStructure(coref=6),
                                                    "+TRAIT":trait_avm,
                                                    "+ID":id_avm,
                                                    "+TNT":tnt_avm})
        token_list_avm = TypedFeatureStructure(type="native_token_cons",
                                               coref=21,
                                               featvals={"FIRST":token_avm,
                                                         "REST":TypedFeatureStructure(type="native_token_null")})
        onset_avm = TypedFeatureStructure(type="con", featvals={"--TL":token_list_avm})
        phon_avm = TypedFeatureStructure(type="phon", featvals={"ONSET":onset_avm})

        ###### PUNCT
        punctuation_avm = TypedFeatureStructure(type="no_punctuation_min",
                                                featvals={"PNCTPR":TypedFeatureStructure(type="ppair")})

        ###### LKEYS
        lkeys_avm = TypedFeatureStructure(type="lexkeys", featvals={"KEYREL":TypedFeatureStructure(coref=7)})

        ###### OTHERS
        sind_avm = TypedFeatureStructure(coref=9)
        min_avm = TypedFeatureStructure(coref=12)

        synsem_avm = TypedFeatureStructure(type="noun_nocomp_synsem",
                                           featvals={"LEX":TypedFeatureStructure(type="+"),
                                                     "OPT":TypedFeatureStructure(type="bool"),
                                                     "NONLOC":non_local_avm,
                                                     "MODIFD":modified_avm,
                                                     "PHON":phon_avm,
                                                     "PUNCT":punctuation_avm,
                                                     "--SIND":sind_avm,
                                                     "--MIN":min_avm,
                                                     "LOCAL":local_avm,
                                                     "LKEYS":lkeys_avm})

        ##### OTHERS
        orth_lb_avm = TypedFeatureStructure(coref=4, type='bracket_null')
        orth_rb_avm = TypedFeatureStructure(coref=5, type='bracket_null')
        orth_to_avm = TypedFeatureStructure(coref=3, type='"12"')
        orth_from_avm = TypedFeatureStructure(coref=2, type='"7"')
        orth_form_avm = TypedFeatureStructure(coref=1, type='"dogs."')
        orth_class_avm = TypedFeatureStructure(coref=6, type="alphabetic",
                                               featvals={"+INITIAL":TypedFeatureStructure(type="-"),
                                                         "+CASE":TypedFeatureStructure(type="non_capitalized+lower")})
        orth_avm = TypedFeatureStructure(type="orthography",
                                         featvals={"FROM":orth_from_avm,
                                                   "FIRST":TypedFeatureStructure(type='"dog"'),
                                                   "FORM":orth_form_avm,
                                                   "TO":orth_to_avm,
                                                   "RB":orth_rb_avm,
                                                   "LB":orth_lb_avm,
                                                   "REST":TypedFeatureStructure(type="*top*"),
                                                   "CLASS":orth_class_avm})
        tokens_avm = TypedFeatureStructure(type="tokens",
                                           featvals={"+LIST":TypedFeatureStructure(coref=21),
                                                     "+LAST":TypedFeatureStructure(coref=22)})

        cls.gold_avm_edge_ID = 20
        cls.goldAvm = TypedFeatureStructure(type="n_-_c_le",
                                            featvals={"ARGS":TypedFeatureStructure(type="*list*"),
                                                      "GENRE":TypedFeatureStructure(type="genre"),
                                                      "DIALECT":TypedFeatureStructure(type="dialect"),
                                                      "KEY-ARG":TypedFeatureStructure(type="bool"),
                                                      "IDIOM":TypedFeatureStructure(type="bool"),
                                                      "RNAME":TypedFeatureStructure(type="basic_ctype"),
                                                      "INFLECTD":TypedFeatureStructure(type="-"),
                                                      "ALTS":TypedFeatureStructure(type="alts_min"),
                                                      "ORTH":orth_avm,
                                                      "SYNSEM":synsem_avm,
                                                      "TOKENS":tokens_avm})
        cls.goldAvm.avm_ID = cls.gold_avm_edge_ID

        cls.gold_avm_string = '''avm 20 #D[n_-_c_le ARGS: *list* ORTH: #D[orthography FIRST: "dog" REST: *top* FORM: <1>= "dogs." FROM: <2>= "7" TO: <3>= "12" LB: <4>= bracket_null RB: <5>= bracket_null CLASS: <6>= #D[alphabetic +INITIAL: - +CASE: non_capitalized+lower ] ] SYNSEM: #D[noun_nocomp_synsem LOCAL: #D[local CONT: #D[nom-obj RELS: #D[*diff-list* LIST: #D[*cons* FIRST: <7>= #D[reg_nom_relation PRED: "_dog_n_1_rel" LBL: <8>= #D[handle INSTLOC: string SORT: *sort* ] ARG0: <9>= #D[ref-ind INSTLOC: string SORT: entity --TPC: luk PNG: #D[png GEN: real_gender PN: pn ] DIV: bool IND: + ] LNK: *list* CFROM: <2> CTO: <3> ] REST: <10>= *list* ] LAST: <10> ] HOOK: #D[hook LTOP: <8> INDEX: <9> XARG: *top* --SLTOP: #D[handle INSTLOC: string SORT: *sort* ] ] HCONS: #D[*diff-list* LIST: <11>= *list* LAST: <11> ] ] CAT: #D[cat HEAD: #D[noun MINORS: #D[minors MIN: <12>= norm_nom_rel ALTMIN: <13>= quant_rel ] --CTYPE: <14>= #D[ctype -CTYPE-: string ] --HID: <15>= string MOD: *null* PRD: bool AUX: luk CASE: case POSS: - --BARE: bool ] VAL: #D[valence_sp SPCMPS: *null* COMPS: <16>= *null* SUBJ: *null* SPR: #D[*cons* FIRST: <17>= #D[synsem LOCAL: #D[local_min1 CAT: #D[cat_min1 HEAD: #D[det MINORS: #D[minors_basic MIN: predsort ] --CTYPE: #D[ctype -CTYPE-: string ] --HID: string MOD: *list* PRD: bool AUX: luk CASE: case POSS: bool --BARE: bool ] VAL: #D[valence COMPS: *list* SUBJ: *null* SPR: *olist* ] ] ] NONLOC: #D[non-local SLASH: <18>= #D[0-1-dlist LIST: *locallist* LAST: *list* ] REL: <19>= #D[0-1-dlist LIST: 0-1-list LAST: *list* ] QUE: <20>= #D[*diff-list* LIST: *list* LAST: *list* ] ] --SIND: *top* OPT: - --MIN: <13> LEX: + MODIFD: xmod_min PHON: phon_min PUNCT: punctuation_min ] REST: *null* ] SPEC: #D[*cons* FIRST: #D[anti_synsem_min LOCAL: mod_local NONLOC: non-local_min ] REST: *null* ] ] MC: na POSTHD: bool HC-LEX: - HS-LEX: - NEGPOL: luk ] ARG-S: #D[*cons* FIRST: <17> REST: <16> ] CONJ: cnil AGR: <9> CTXT: ctxt_min ] LKEYS: #D[lexkeys KEYREL: <7> ] NONLOC: #D[non-local SLASH: <18> REL: <19> QUE: <20> ] --SIND: <9> OPT: bool --MIN: <12> LEX: + MODIFD: #D[notmod LPERIPH: luk RPERIPH: luk ] PHON: #D[phon ONSET: #D[con --TL: <21>= #D[native_token_cons FIRST: <22>= #D[token +FORM: <1> +FROM: <2> +TO: <3> +ID: #D[*diff-list* LIST: *list* LAST: *list* ] +TNT: #D[null_tnt +TAGS: *null* +PRBS: *null* +MAIN: #D[tnt_main +TAG: "NNS" +PRB: "1.0" ] ] +CLASS: <6> +TRAIT: #D[token_trait +UW: - +IT: italics +LB: <4> +RB: <5> +HD: #D[token_head +LL: <14> +TG: <15> ] ] +PRED: predsort +CARG: "dogs" +TICK: bool ] REST: native_token_null ] ] ] PUNCT: #D[no_punctuation_min PNCTPR: ppair ] ] TOKENS: #D[tokens +LIST: <21> +LAST: <22> ] KEY-ARG: bool INFLECTD: - GENRE: genre DIALECT: dialect IDIOM: bool RNAME: basic_ctype ALTS: alts_min ] "edge"'''



    def setUp(self):
        # TODO: Standardize this path
        self.parser = InteractiveAce("~/delphin/erg.dat")
        self.text = "I run"


    # Basic tests
    def testParse(self):
        result = lui.parse(__class__.parser, __class__.text)
        self.assertEqual(result['SENT'], __class__.text)
        self.assertEqual(len(result['RESULTS']), 1)
        self.assertEqual(Derivation(result['RESULTS'][0]), Derivation('#T[1 "XP" nil 582 np_nb-frg_c #T[2 "N" nil 581 np-hdn_cpd_c #T[3 "NP" nil 578 hdn_bnp-pn_c #T[4 "N" "I" 64 i_pn_np1]] #T[5 "N" nil 580 hdn_optcmp_c #T[6 "N" nil 579 n_sg_ilr #T[7 "N" "run" 39 run_n1]]]]]'))


    @unittest.skip
    def testGenerate(self):
        self.fail("Need to implement Generate()!")


    def testParseToMrs(self):
        tree = lui.parse(self.parser, __class__.goldText)
        # Request MRS
        lui.request_mrs(self.parser, 1, 1)
        mrs_string = lui.receive_mrs(self.parser)
        mrs = lui.load_mrs(mrs_string)
        self.assertTrue(isomorphic(__class__.goldMrs, mrs))

    
    def testParseToAvm(self):
        tree = lui.parse(self.parser, __class__.goldText)
        # Request AVM
        lui.request_avm(self.parser, 1, 10)
        avm_string = lui.receive_avm(self.parser)
        avm = lui.load_avm(avm_string)
        self.assertEqual(avm, __class__.goldAvm)


    # Request tests
    def testRequestParse(self):
        lui.request_parse(__class__.parser, __class__.text)
        expectation = [re.compile(r"parse .*?\r\n")]
        self.assertEqual(__class__.parser._p.expect(expectation), 0)


    def testRequestMRS(self):
        # Request / process parse
        lui.request_parse(self.parser, __class__.goldText)
        lui.receive_derivations(self.parser, __class__.goldText)
        # Request MRS
        lui.request_mrs(self.parser, 1, 1)
        expectation = [re.compile(r"avm .*?\r\n")]
        self.assertEqual(self.parser._p.expect(expectation), 0)


    def testRequestAVM(self):
        self.parser._p.sendline("parse {}.\f".format(__class__.goldText))
        lui.receive_derivations(self.parser, __class__.goldText)
        # Request AVM
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
        __class__.parser._p.sendline("parse {}\f".format(__class__.goldText))
        response = lui.receive_derivations(__class__.parser, __class__.goldText)
        self.assertEqual(response['SENT'], __class__.goldText)
        self.assertEqual(len(response['RESULTS']), 2)
        # TODO: Need to add mock object to compare


    def testReceiveMRS(self):
        # Request / process parse
        lui.request_parse(self.parser, __class__.goldText)
        lui.receive_derivations(self.parser, __class__.goldText)
        # Request MRS
        lui.request_mrs(self.parser, 1, 1)
        # Receive MRS
        response = lui.receive_mrs(self.parser)
        tag = response.split(None, 1)[0]
        sort = response.rsplit('"', 2)[-2]
        self.assertEqual(tag, "avm")
        self.assertEqual(sort, "Simple MRS")


    def testReceiveAVM(self):
        # Request / process parse
        lui.request_parse(self.parser, __class__.goldText)
        lui.receive_derivations(self.parser, __class__.goldText)
        # Request AVM
        lui.request_avm(self.parser, 1, 1)
        # Receive AVM
        response = lui.receive_avm(self.parser)

    
    @unittest.skip
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
        result = lui.load_avm(__class__.gold_avm_string)
        import sys
        #print("GENERATED:", file=sys.stderr)
        #print(result, file=sys.stderr)
        #print("\n"*3)
        #print("LOADED:", file=sys.stderr)
        #print(__class__.goldAvm, file=sys.stderr)
        self.assertEqual(__class__.goldAvm, result)


    ## MRS Tests
    def testLoadMrs(self):
        # MRS for "I like dogs." from ERG 1212
        result = lui.load_mrs(__class__.gold_mrs_string)
        self.assertTrue(isomorphic(__class__.goldMrs, result))

    

    def testLoadMrsOther(self):
        result = lui.load_mrs(__class__.other_mrs_string)
        # converted = lui._convert_lui_mrs_to_simple_mrs(__class__.other_mrs_string)
        # print(converted)
        # result = simplemrs.loads_one(converted)
        # print(result)
        self.assertEqual("h0", result.top)
        

    def testLoadMrsThird(self):
        result = lui.load_mrs(__class__.third_mrs_string)
        self.assertEqual("h0", result.top)
        

    def testConvertLuiMrsToSimpleMrs(self):
        target = ['[', 'TOP', ':', 'h0', 'INDEX', ':', 'e2', '[', 'e', 'SF', ':', 'prop', 'TENSE', ':', 'pres', 'MOOD', ':', 'indicative', 'PROG', ':', '-', 'PERF', ':', '-', ']', 'RELS', ':', '<', '[', 'pron_rel', 'LBL', ':', 'h4', 'ARG0', ':', 'x3', '[', 'x', 'PERS', ':', '1', 'NUM', ':', 'sg', 'PRONTYPE', ':', 'std_pron', ']', ']', '[', 'pronoun_q_rel', 'LBL', ':', 'h5', 'ARG0', ':', 'x3', '[', 'x', 'PERS', ':', '1', 'NUM', ':', 'sg', 'PRONTYPE', ':', 'std_pron', ']', 'RSTR', ':', 'h6', 'BODY', ':', 'h7', ']', '[', '"_like_v_1_rel"', 'LBL', ':', 'h1', 'ARG0', ':', 'e2', '[', 'e', 'SF', ':', 'prop', 'TENSE', ':', 'pres', 'MOOD', ':', 'indicative', 'PROG', ':', '-', 'PERF', ':', '-', ']', 'ARG1', ':', 'x3', '[', 'x', 'PERS', ':', '1', 'NUM', ':', 'sg', 'PRONTYPE', ':', 'std_pron', ']', 'ARG2', ':', 'x8', '[', 'x', 'PERS', ':', '3', 'NUM', ':', 'pl', 'IND', ':', '+', ']', ']', '[', 'udef_q_rel', 'LBL', ':', 'h9', 'ARG0', ':', 'x8', '[', 'x', 'PERS', ':', '3', 'NUM', ':', 'pl', 'IND', ':', '+', ']', 'RSTR', ':', 'h10', 'BODY', ':', 'h11', ']', '[', '"_dog_n_1_rel"', 'LBL', ':', 'h12', 'ARG0', ':', 'x8', '[', 'x', 'PERS', ':', '3', 'NUM', ':', 'pl', 'IND', ':', '+', ']', ']', '>', 'HCONS', ':', '<', 'h0', 'qeq', 'h1', 'h6', 'qeq', 'h4', 'h10', 'qeq', 'h12', '>', ']']
        result = lui._convert_lui_mrs_to_simple_mrs(__class__.gold_mrs_string)
        self.assertEqual(tokenize(result), target)


    # Dump tests
    def testDumpTree(self):
        pass


    def testDumpAVM(self):
        pass


    def testDumpMRS(self):
        pass
