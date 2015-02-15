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
        ace = TestInteractiveAce.ace

        #self.assertEqual(ace.parse(""), "No parse found for \"\".")
        #self.assertEqual(ace.parse("Dog big home."), "No parse found for \"dog big home.\".")
        self.assertEqual(ace.parse("I run."), "")
        

    def test_send_parse(self):
        self.assertTrue(false)

    def test_receive_parse(self):
        self.assertTrue(false)

    
class FakePexpect(object):
        
    def __init__(self):
        pass
