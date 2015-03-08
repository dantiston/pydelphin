import unittest

# NEED TO MOVE avm.tokenize() TO lui.py#read_avm()

from delphin.avm import avm

class avmTest(unittest.TestCase):

    def setUp(self):
        self.basic_lui_avm = "#D[orthog FIRST: *top* REST: *top* FORM: string FROM: <1>= \"0\" TO: <2>= \"6\" LB: <3>= bracket_null RB: <4>= bracket_null ]"
        self.nested_lui_avm = "#D[frag_vp_fin_rule ORTH: #D[orthog FIRST: *top* REST: *top* FORM: string FROM: <1>= \"0\" TO: <2>= \"6\" LB: <3>= bracket_null RB: <4>= bracket_null ] ]"

    def test_init(self):
        pass
    
    def test_tokenize(self):
        expected = ["#D[", "orthog", "FIRST", ":", "*top*", "REST", ":", "*top*", "FORM", ":", "string", "FROM", ":", "<1>", "=", "\"0\"", "TO", ":", "<2>", "=", "\"6\"", "LB", ":", "<3>", "=", "bracket_null", "RB", ":", "<4>", "=", "bracket_null", "]"]
        self.assertEqual(list(avm.tokenize(self.basic_lui_avm)), expected)

    def test_tokenize_nested(self):
        expected = ["#D[", "frag_vp_fin_rule", "ORTH", ":", "#D[", "orthog", "FIRST", ":", "*top*", "REST", ":", "*top*", "FORM", ":", "string", "FROM", ":", "<1>", "=", "\"0\"", "TO", ":", "<2>", "=", "\"6\"", "LB", ":", "<3>", "=", "bracket_null", "RB", ":", "<4>", "=", "bracket_null", "]", "]"]
        self.assertEqual(list(avm.tokenize(self.nested_lui_avm)), expected)





