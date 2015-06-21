"""
lui.py

This set of functions takes an interactive parser as a parameter and runs commands with its data members.
An interactive parser must have a pexpect object at ._p open and waiting for a LUI command.

For more information on pexpect, see http://pexpect.readthedocs.org/en/latest/

Interface for interacting with a LUI protocol
    * For communicating with a parser:
        * parse(): send the parse command and request output trees
        * generate(): send the generate command and request output sentences

    * For sending information to a parser:
        * request_parse(): send the parse command to a parser to request derivations
        * request_mrs(): send the request command to a parser to request an mrs of a given chart ID
        * request_avm(): send the request command to a parser to request an avm of a given chart ID
        * request_generate(): send the generate command to a parser to request sentences
        * request_unify(): send the unify command to a parser to request a unification of two chart IDs

    * For receiving information from a parser:
        * receive_derivations(): receive a list of derivation trees from a parser
        * receive_mrs(): receive a list of mrs from a parser
        * receive_avm(): receive a list of avm from a parser
        * receive_sentences(): receive a list of sentences from a parser

    * For deserializing and serializing LUI data structures:
        * load_derivations(): deserializes LUI tree string into PyDelphin Derivation object
        * load_avm(): deserializes LUI AVM string into PyDelphin AVM object
        * load_mrs(): deserializes LUI MRS string into PyDelphin MRS object
        * dump_tree(): serializes PyDelphin Derivation object into LUI tree string
        * dump_avm(): serializes PyDelphin AVM structure into LUI AVM string
        * dump_mrs(): serializes PyDelphin MRS structure into LUI MRS string

# Author: T.J. Trimble <trimblet@me.com>
"""

import re
import pexpect

from collections import defaultdict

# PyDelphin imports
## Data structures
from ..derivation import Derivation
from ..mrs import simplemrs
from ..mrs.components import MrsVariable, HandleConstraint, ElementaryPredication, Pred, Argument, Hook
from ..tfs import TypedFeatureStructure
## Methods
from ..tdl import tokenize as avm_tokenize

# Constants
dag_bracket = "#D["
tree_bracket = "#T["
close_bracket = "]"

# Utility Functions
def _compile_tag_template(tag_template):
    result = []
    for item in tag_template:
       if isinstance(item, str):
           result.append(re.compile(item))
       else:
           result.append(item)
    return result


# Basic functions
def parse(parser, datum):
    if not datum.strip():
        return {'SENT': "", 'RESULTS': []}
    request_parse(parser, datum)
    return receive_derivations(parser, datum)


def generate(parser, mrs):
    if not mrs.strip():
        return {'SENT': "", 'RESULTS': []}
    self._request_generate(datum)
    return self._receive_sentences(datum)


# Request and browse commands
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


# Receive commands
## Derivation commands
def _pass(parser, datum=""):
    pass


def _extract_parse_count(parser, datum=""):
    """
    Expected format:
        group <count> "<text>"
    """
    match = parser._p.after.split(None, 2)
    if match[0] != "group":
        raise Exception("Something bad happened at {}#_extract_parse_count()".format(__name__))
    text = match[2]
    if datum not in text:
        raise Exception("The parse input is not in the parse output at {}#_extract_parse_count()".format(__name__))
    return int(match[1])


def _extract_parse(parser):
    """
    Expected format:
    \tree <tree_ID> #T[<edge_ID> "<label>" "<token>" <chart_ID> <rule_name> (#T[.*])?] "<text>"\
    """

    return parser._p.after


def _no_parse(parser, datum=""):
    return 0, "No parse found for {}.".format(datum)


def _raise_exception(parser, datum=""):
    exception = parser._p.after
    raise Exception("\n".join([exception, str(parser._p)]))

# Header actions
derivation_header_tag_template = [
    r"parse .*?\r\n", # 0
    r"group .*?\r\n", # 1
    r"SKIP: .*?\r\n", # 2
    r"LUI: unknown .*\r\n", # 3
    pexpect.EOF, # 4
    pexpect.TIMEOUT, # 5
]

derivation_header_tags = _compile_tag_template(derivation_header_tag_template)

derivation_header_actions = {
    0:_pass,
    1:_extract_parse_count,
    2:_no_parse,
    3:_no_parse,
    4:_raise_exception,
    5:_raise_exception, # TODO: Something different
}

# Result actions
derivation_result_tag_template = [
    r"tree .*?\r\n", # 0
    r"LUI: unknown .*?\r\n", # 1
    r"LUI: out-of-date .*?\r\n", #2
    pexpect.EOF, # 3
    pexpect.TIMEOUT, # 4
]

derivation_result_actions = {
    0:_extract_parse,
    1:_no_parse,
    2:_raise_exception,
    3:_no_parse,
    4:_raise_exception, # TODO: Something different
}

derivation_result_tags = _compile_tag_template(derivation_result_tag_template)


def receive_derivations(parser, datum):
    """
    Use pexpect to receive text output of derivation trees from parser in LUI mode
    """
    result = []
    blank = 0
    response = {
        'SENT': datum.strip('"'),
        'RESULTS': []
    }

    # Get parse count
    # TODO: Figure out what to do if ACE output malformed?
    parse_count = -1
    while parse_count < 0:
        ID = parser._p.expect(derivation_header_tags)
        result = derivation_header_actions[ID](parser, datum=datum)
        if result:
            parse_count = result

    # Get parses
    for i in range(parse_count):
        ID = parser._p.expect(derivation_result_tags, timeout=10)
        response['RESULTS'].append(derivation_result_actions[ID](parser))

    return response


## AVM/MRS commands
def _extract_avm(parser):
    """
    Format:
        avm <avm_ID> #D[mrs TOP: <coref>=#D[.*] INDEX: <coref>=#D[.*] RELS: #D[.*] HCONS: #D[.*] (ICONS: #D[.*])?] "Simple MRS"
    """
    return parser._p.after

avm_header_tag_template = [
    r"browse .*?\r\n", # 0
    pexpect.EOF, # 2
    pexpect.TIMEOUT, # 3
]

avm_header_tags = _compile_tag_template(avm_header_tag_template)

avm_header_actions = {
    0:_pass,
    1:_raise_exception,
    2:_raise_exception, # TODO: Something different for timeout
}

# Result actions
avm_result_tag_template = [
    r"avm .*?\r\n", # 0
    r"LUI: unknown .*?\r\n", # 1
    r"LUI: out-of-date .*?\r\n", #2
    pexpect.EOF, # 3
    pexpect.TIMEOUT, # 4
]

avm_result_actions = {
    0:_extract_avm,
    1:_no_parse,
    2:_raise_exception,
    3:_no_parse,
    4:_raise_exception, # TODO: Something different
}

avm_result_tags = _compile_tag_template(avm_result_tag_template)


def receive_mrs(parser):
    """
    Use pexpect to receive text output of MRS from parser in LUI mode
    """
    header_ID = parser._p.expect(avm_header_tags, timeout=1)
    ID = parser._p.expect(avm_result_tags, timeout=1)
    response = avm_result_actions[ID](parser)
    return response


def receive_avm(parser):
    return receive_mrs(parse)


# Pickle API
## Load commands
### Derivation commands
strip_quotes = re.compile("^[\'\"]|[\'\"]$")
legal_punctuation = re.escape("'’-+=/:.!?$<>@#%^&*")
lui_derivation_pattern = " ".join(("(?P<EDGE_ID>\d+)",
                                   "(?P<LABEL>{quote}[\w{punc}]+{quote})",
                                   "(?P<TOKEN>({quote}[\w{punc}]+{quote}|nil))",
                                   "(?P<CHART_ID>\d+)",
                                   "(?P<RULE_NAME>[\w{punc}]+)",)).format(
                                       quote="[\'\"]?",
                                       punc=legal_punctuation)


tree_prefix = "tree "
def load_derivations(string):
    """
    Deserializes LUI tree string into PyDelphin Derivation objects

    Based on NLTK's Tree.fromstring():
        http://www.nltk.org/_modules/nltk/tree.html#Tree.fromstring

    Format:
        (tree <tree_ID> #T[<edge_ID> "?<label>"? ("<token>"|nil) <chart_ID> <rule_name> (#T[.*])?] "<text>"\n\n)*

    """
    newlines = re.compile(r"\n{2,}")
    result = []
    for s in newlines.split(string):
        s = s.strip()
        # Parse introduction
        if s.startswith(tree_prefix):
            _, tree_ID, s = s.split(None, 2)
            if s.endswith('"'): # Only do this if there's a quote at the end
                s = s.rsplit('"', 2)[0].strip() # assumes no quote in text
        else:
            tree_ID = None
        # Initialize bracket pointers
        open_pattern, close_pattern = (re.escape(tree_bracket), re.escape(close_bracket))
        # Leaves and nodes contain non-whitespace, non-bracket characters
        valid_chars = '[^\s%s%s]+' % (open_pattern, close_pattern)
        bracket_patterns = '[%s%s]+' % (open_pattern, close_pattern)
        # Construct a regexp that will tokenize the string.
        token_re = re.compile('%s%s|%s|(%s)' % (
            open_pattern, lui_derivation_pattern, close_pattern, valid_chars))
        # Walk through each token, updating a stack of trees.
        stack = [(None, [])] # list of (node, children) tuples
        tokens = list(token_re.finditer(s))
        for i, match in enumerate(tokens):
            token = match.group()
            # Definition of a tree/subtree
            #  #T[EDGE_ID LABEL TOKEN CHART_ID RULE_NAME
            if token.startswith(tree_bracket):
                if len(stack) == 1 and len(stack[0][1]) > 0:
                    _parse_error(s, match, 'end-of-string')
                edge_ID = match.group('EDGE_ID')
                label = match.group('LABEL')
                token = match.group('TOKEN')
                chart_ID = match.group('CHART_ID')
                rule_name = match.group('RULE_NAME')
                stack.append(((edge_ID, label, token, chart_ID, rule_name), []))
            # End of a tree/subtree
            elif token == close_bracket:
                if len(stack) == 1:
                    if len(stack[0][1]) == 0:
                        _parse_error(s, match, tree_bracket)
                    else:
                        _parse_error(s, match, 'end-of-string')
                data, children = stack.pop()
                stack[-1][1].append(Derivation(None, data_package=data, children=children))
            # Leaf node
            else:
                if len(stack) == 1:
                    _parse_error(s, match, tree_bracket)
                stack[-1][1].append(token)

        # check that we got exactly one complete tree.
        if len(stack) > 1:
            _parse_error(s, 'end-of-string', close_bracket)
        elif len(stack[0][1]) == 0:
            _parse_error(s, 'end-of-string', tree_bracket)
        else:
            assert stack[0][0] is None
            assert len(stack[0][1]) == 1
        tree = stack[0][1][0]

        # Get tree ID
        tree.tree_ID = tree_ID
        result.append(tree)

    return result

# Loading AVM
lui_avm_pattern = " ".join(("(?P<TYPE_NAME>[\w{punc}]+)",
                            "(?P<RULE_NAME>[\w{punc}]+)",)).format(
                                punc=legal_punctuation)


avm_prefix = "avm "
avm_suffix = " \"edge\""
avm_key_seperator = ":"

last_i = -1
first_i = 0
type_i = 0
features_i = 1
key_i = 2
children_i = 3

def load_avm(avm_string):
    """
    deserializes LUI AVM string into PyDelphin TypedFeatureStructure object

    format:
        (avm <avm_ID> )?#D[<type_name> (<key>: (<coref>= )?<value>)* ]( "edge")
    """

    if dag_bracket not in avm_string:
        return TypedFeatureStructure()
    avm_string = avm_string.strip()

    # Parse introduction
    if avm_string.startswith(avm_prefix):
        _, avm_ID, avm_string = avm_string.split(None, 2)
        if avm_string.endswith(avm_suffix): # Only do this if there's a quote at the end
            avm_string = avm_string.rsplit('"', 2)[0].strip() # assumes no quote in text
    else:
        avm_ID = -1
    # Initializations
    open_pattern, close_pattern = (re.escape(dag_bracket), re.escape(close_bracket))
    type_name = None
    key = None
    next_is_value = False
    next_is_coreferenced = False
    # Leaves and nodes contain non-whitespace, non-bracket characters
    valid_chars = '[^\s%s%s]+' % (open_pattern, close_pattern)
    bracket_patterns = '[%s%s]+' % (open_pattern, close_pattern)
    # Construct a regexp that will tokenize the string.
    token_re = re.compile('%s%s|%s|(%s)' % (
        open_pattern, lui_avm_pattern, close_pattern, valid_chars))
    # Walk through each token, updating a stack of trees.
    stack = [(type_name, {}, key, [])] # list of (node, featurevals, key, children) tuples
    tokens = avm_string.split()

    # with open("/home/dantiston/Desktop/output.txt", "w") as output:
    #     for i, token in enumerate(tokens):
    #         #print(token, file=output)
    #         # Beginning of AVM
    #         if token.startswith(dag_bracket):
    #             if len(stack) == 1 and len(stack[first_i][children_i]) > 0:
    #                 _parse_error(s, token, 'end-of-string')
    #             stack.append((token[len(dag_bracket):], {}, key, []))
    #             #print("STORING: {type_name: %s, featvals: %s, key: %s, children: %s}" % (token[len(dag_bracket):], {}, key, []), file=output)
    #         # End bracket
    #         elif token == close_bracket:
    #             #print("PROCESSING END OF AVM", file=output)
    #             if len(stack) == 1:
    #                if len(stack[first_i][children_i]) == 0:
    #                    _parse_error(avm_string, token, dag_bracket)
    #                else:
    #                    _parse_error(avm_string, token, 'end-of-string')
    #             type_name, featvals, key, children = stack.pop()
    #             #print("Requesting TFS: {type: %s, featvals: %s}" % (type_name, featvals), file=output)
    #             tfs = TypedFeatureStructure(type=type_name, featvals=featvals)
    #             #print("Built TFS: " + str(key), file=output)
    #             if len(stack) > 1: # THIS IS THE END OF A VALUE, ADD THE AVM TO THE FEATURES DICTIONARY
    #                 stack[last_i][features_i][key] = tfs
    #             else: # THIS IS THE END OF THE OVERALL AVM, PUT THE AVM ON THE TOP'S LIST
    #                 stack[last_i][children_i].append(tfs)
    #             #print("CONSTRUCTING TFS: {type_name: %s, featvals: %s, key: %s, children: %s}" % (type_name, featvals, key, children), file=output)
    #         # Key
    #         elif token.endswith(avm_key_seperator):
    #             key = token[:-len(avm_key_seperator)]
    #             next_is_value = True
    #             continue
    #         # Value
    #         elif next_is_value:
    #             # Coreference
    #             if is_coreference_tag(token):
    #                 next_is_coreferenced = True
    #             else:
    #                 # Keep track of coreference
    #                 if next_is_coreferenced:
    #                     pass # TODO: This
    #                 # For now, store coreferences as strings
    #                 # TODO: Figure out what to do with coreferences
    #                 elif is_coreference_value(token):
    #                     pass
    #                 next_is_coreferenced = False
    #                 # SubAVM
    #                 if token.startswith(dag_bracket):
    #                     if len(stack) == 1 and len(stack[first_i][children_i]) > 0:
    #                         _parse_error(avm_string, token, 'end-of-string')
    #                     #stack.append((token[len(dag_bracket):], featvals, []))
    #                     stack.append((token[len(dag_bracket):], {}, key, []))
    #                     #print("STORING: {type_name: %s, featvals: %s, key: %s, children: %s}" % (token[len(dag_bracket):], {}, key, []), file=output)
    #                 # String
    #                 else:
    #                     stack[last_i][features_i][key] = token
    #                 next_is_value = False
    #         # Out of place coreference
    #         elif is_coreference_tag(token):
    #             _parse_error(avm_string, token, "KEY or " + close_bracket)
    #         # Boolean
    #         else:
    #             stack[last_i][features_i][token] = True

    for i, token in enumerate(tokens):
        #print(token, file=output)
        # Beginning of AVM
        if token.startswith(dag_bracket):
            if len(stack) == 1 and len(stack[first_i][children_i]) > 0:
                _parse_error(s, token, 'end-of-string')
            stack.append((token[len(dag_bracket):], {}, key, []))
            #print("STORING: {type_name: %s, featvals: %s, key: %s, children: %s}" % (token[len(dag_bracket):], {}, key, []), file=output)
        # End bracket
        elif token == close_bracket:
            #print("PROCESSING END OF AVM", file=output)
            if len(stack) == 1:
               if len(stack[first_i][children_i]) == 0:
                   _parse_error(avm_string, token, dag_bracket)
               else:
                   _parse_error(avm_string, token, 'end-of-string')
            type_name, featvals, key, children = stack.pop()
            #print("Requesting TFS: {type: %s, featvals: %s}" % (type_name, featvals), file=output)
            tfs = TypedFeatureStructure(type=type_name, featvals=featvals)
            #print("Built TFS: " + str(key), file=output)
            if len(stack) > 1: # THIS IS THE END OF A VALUE, ADD THE AVM TO THE FEATURES DICTIONARY
                stack[last_i][features_i][key] = tfs
            else: # THIS IS THE END OF THE OVERALL AVM, PUT THE AVM ON THE TOP'S LIST
                stack[last_i][children_i].append(tfs)
            #print("CONSTRUCTING TFS: {type_name: %s, featvals: %s, key: %s, children: %s}" % (type_name, featvals, key, children), file=output)
        # Key
        elif token.endswith(avm_key_seperator):
            key = token[:-len(avm_key_seperator)]
            next_is_value = True
            continue
        # Value
        elif next_is_value:
            # Coreference
            if is_coreference_tag(token):
                next_is_coreferenced = True
            else:
                # Keep track of coreference
                if next_is_coreferenced:
                    pass # TODO: This
                # For now, store coreferences as strings
                # TODO: Figure out what to do with coreferences
                elif is_coreference_value(token):
                    pass
                next_is_coreferenced = False
                # SubAVM
                if token.startswith(dag_bracket):
                    if len(stack) == 1 and len(stack[first_i][children_i]) > 0:
                        _parse_error(avm_string, token, 'end-of-string')
                    #stack.append((token[len(dag_bracket):], featvals, []))
                    stack.append((token[len(dag_bracket):], {}, key, []))
                    #print("STORING: {type_name: %s, featvals: %s, key: %s, children: %s}" % (token[len(dag_bracket):], {}, key, []), file=output)
                # String
                else:
                    stack[last_i][features_i][key] = token
                next_is_value = False
        # Out of place coreference
        elif is_coreference_tag(token):
            _parse_error(avm_string, token, "KEY or " + close_bracket)
        # Boolean
        else:
            stack[last_i][features_i][token] = True


    # check that we got exactly one complete avm
    if len(stack) > 1:
        _parse_error(avm_string, 'end-of-string', close_bracket)
    elif len(stack[first_i][children_i]) == 0:
        _parse_error(avm_string, 'end-of-string', dag_bracket)
    else:
        assert stack[first_i][type_i] is None
        assert stack[first_i][key_i] is None
        assert len(stack[first_i][children_i]) == 1
    avm = stack[first_i][children_i][0]

    # Get AVM ID
    #avm.avm_ID = avm_ID

    #print("AVM: " + str(avm._avm), file=output)
    #print(avm._avm, file=sys.stderr)

    return avm


def is_coreference_tag(string):
    """
    Identifies coreference tags is the following format:
        "<{int}>"

    where {int} must be a digit
    """
    return string.endswith("=") and is_coreference_value(string[:-1])


def is_coreference_value(string):
    """
    Identifies coreference values in the following format:
        "<{int}>"

    where {int} must be a digit
    """
    return string.startswith("<") and string.endswith(">") and string[1:-1].isdigit()


## MRS
# For mrs conversion
def _var_repl(match):
    """
    @author: Michael Wayne Goodman
    """
    varstring = '{}{}'.format(match.group('sort'), match.group('vid'))
    if match.group('rest'):
        varstring = '{} [{} {}]'.format(
            varstring,
            match.group('sort'),
            match.group('rest').replace('"', '')
        )
    return varstring


def _xcons_repl(match):
    """
    @author: Michael Wayne Goodman
    """
    return '{}: < {} >'.format(
        match.group(1),
        re.sub(r'#D\[\s*(\S+)\s*\S+:\s*(\S+)\s+\S+:\s*(\S+)\s*\]',
               r'\2 \1 \3',
               match.group(2))
    )


def _clean_lui_mrs(mrs_string, sort="Simple MRS"):
    mrs_string = mrs_string.strip().rstrip("^L") # Strip whitespace, line feed
    if mrs_string.startswith("avm "):
        mrs_string = mrs_string.split(None, 2)[-1]
    if mrs_string.endswith(' "{}"'.format(sort)):
        mrs_string = mrs_string.rsplit(None, 2)[0]
    return mrs_string


def _convert_lui_mrs_to_simple_mrs(mrs_string):
    """
    @author: Michael Wayne Goodman, T.J. Trimble
    """
    # strip header and footer
    mrs_string = _clean_lui_mrs(mrs_string)
    # get rid of the top MRS type
    s = re.sub(r'#D\[mrs', '[', mrs_string)
    # reformat variables and their properties
    s = re.sub(
        r'<(?P<vid>\d+)>=#D\[(?P<sort>[^ \]]+)(?P<rest>[^\]]*)\]',
        _var_repl,
        s
    )
    # change the cons-lists to SimpleMRS lists
    s = re.sub(r'(RELS|HCONS|ICONS):\s*#D\[\*cons\*\s*FIRST:', r'\1: <', s)
    s = re.sub(r'REST:\s*#D\[\*null\*\](\s*\])*', '>', s)
    s = re.sub(r'REST:\s*#D\[\*cons\*\s*FIRST:', '', s)
    # reformat HCONS and ICONS
    s = re.sub(r'(HCONS|ICONS):\s*<([^>]*)>', _xcons_repl, s)
    # reformat string values like CARG
    s = re.sub(r'(\S+):\s*"(.*?)" ', r'\1: \2 ', s)
    # remove any remaining #Ds
    s = re.sub(r'#D', '', s)
    # and re-add the last ] which was lost during cons-list conversion
    s = s + ' ]'
    return s


def load_mrs(mrs_string):
    """
    deserializes LUI MRS string into PyDelphin MRS object

    Format:
        #D[mrs TOP: <coref>=#D[<argument_label>]
               INDEX: <coref>=#D[.*]
               RELS: #D[<list<ElementaryPredication>>]
               HCONS: #D[<list<HandleConstraint>>]
               ICONS: #D[<list<IndividualConstraint>>]
        ]
    """

    return simplemrs.loads_one(_convert_lui_mrs_to_simple_mrs(mrs_string))


# Dump commands
def dump_tree():
    # TODO: this
    """
    serializes PyDelphin Derivation object into LUI tree string
    """
    pass


def dump_avm():
    # TODO: this
    """
    serializes PyDelphin AVM structure into LUI AVM string
    """
    pass


def dump_mrs():
    # TODO: this
    """
    serializes PyDelphin MRS structure into LUI MRS string
    """
    pass



# Errors
def _parse_error(s, match, expecting):
    """
    Raise an error from load_derivations() & load_avm()

    From NLTK: http://www.nltk.org/_modules/nltk/tree.html
    """
    # Construct a basic error message
    if isinstance(match, str):
        pos, token = len(s), match
    else:
        pos, token = match.start(), match.group()
    msg = 'lui: expected %r but got %r\n%sat index %d.' % (
           expecting, token, ' '*12, pos)
    # Add a display showing the error token itsels:
    s = s.replace('\n', ' ').replace('\t', ' ')
    offset = pos
    if len(s) > pos+10:
        s = s[:pos+10]+'...'
    if pos > 10:
        s = '...'+s[pos-10:]
        offset = 13
    msg += '\n%s"%s"\n%s^' % (' '*16, s, ' '*(17+offset))
    raise ValueError(msg)
