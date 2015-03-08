"""
lui.py

Interface for interacting with a LUI protocol
    * For sending information to a parser:
        * request_parse(): send the parse command to a parser to request a derivation
        * request_mrs(): send the request command to a parser to request an mrs of a given chart ID
        * request_avm(): send the request command to a parser to request an avm of a given chart ID

    * For receiving information from a parser:
        * receive_tree(): receive a derivation tree from a parser
        * receive_mrs(): receive an mrs from a parser
        * receive_avm(): receive an avm from a parser

    * For deserializing and serializing LUI data structures:
        * load_tree(): deserializes LUI tree string into PyDelphin Derivation object
        * load_avm(): deserializes LUI AVM string into PyDelphin AVM object
        * load_mrs(): deserializes LUI MRS string into PyDelphin MRS object
        * dump_tree(): serializes PyDelphin Derivation object into LUI tree string
        * dump_avm(): serializes PyDelphin AVM structure into LUI AVM string
        * dump_mrs(): serializes PyDelphin MRS structure into LUI MRS string

This set of functions takes an interactive parser as a parameter and runs commands with its data members.
An interactive parser must have a pexpect object at ._p open and waiting for a LUI command.

For more information on pexpect, see http://pexpect.readthedocs.org/en/latest/

@author T.J. Trimble
"""

def _browse(parser, tree_ID, edge_ID, what):
    parser._p.sendline('browse {tree_ID} {edge_ID} {what}\f'.format(tree_ID=tree_ID, edge_ID=edge_ID, what=what))


def request_parse(parser, datum):
    """
    Send the parse command to the given parser with the given datum
    """
    parser._p.sendline('parse {}\f'.format(datum.rstrip()))


def request_mrs(parser, tree_ID, chart_ID):
    """
    Send the browse command to the given parser to request the MRS for the given tree_ID, chart_ID
    """
    _browse(parser, tree_ID, chart_ID, "mrs simple")


def request_avm(parser, tree_ID, chart_ID):
    """
    Send the browse command to the given parser to request the AVM for the given tree_ID, chart_ID
    """
    _browse(parser, tree_ID, chart_ID, "avm")
                
                
def receive_tree(parser):
    """
    Format:
        tree <tree_ID> #T[<edge_ID> "?<label>"? ("<token>"|nil) <chart_ID> <rule_name> (#T[.*])?] "<text>"
    """
    tree = ""

    return tree
                    
                    
def receive_mrs(parser):
    """
    Format:
        avm <avm_ID> #D[mrs TOP: <coref>=#D[.*] INDEX: <coref>=#D[.*] RELS: #D[.*] HCONS: #D[.*] (ICONS: #D[.*])?] "Simple MRS"
    """
    mrs = ""
    return mrs


def receive_avm(parser):
    """
    Format:
        avm <avm_ID> #D[.*] "edge"
    """
    avm = ""
    return avm


def load_tree():
    """
    deserializes LUI tree string into PyDelphin Derivation object
    """
    pass


def load_avm():
    """
    deserializes LUI AVM string into PyDelphin AVM object
    """
    pass


def load_mrs():
    """
    deserializes LUI MRS string into PyDelphin MRS object
    """
    pass


def dump_tree():
    """
    serializes PyDelphin Derivation object into LUI tree string
    """
    pass


def dump_avm():
    """
    serializes PyDelphin AVM structure into LUI AVM string
    """
    pass


def dump_mrs():
    """
    serializes PyDelphin MRS structure into LUI MRS string
    """
    pass

