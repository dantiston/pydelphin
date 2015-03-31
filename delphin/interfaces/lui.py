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

@author T.J. Trimble
"""

import re
import pexpect

from collections import defaultdict

# PyDelphin imports
## Data structures
from ..derivation import Derivation
from ..mrs.xmrs import Mrs
from ..mrs.components import MrsVariable, HandleConstraint, ElementaryPredication, Pred, Argument, Hook
## Methods
from ..tdl import tokenize as avm_tokenize

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
    raise exception(str(parser._p))

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


## MRS commands
def _extract_mrs(parser):
    """
    Format:
        avm <avm_ID> #D[mrs TOP: <coref>=#D[.*] INDEX: <coref>=#D[.*] RELS: #D[.*] HCONS: #D[.*] (ICONS: #D[.*])?] "Simple MRS"
    """
    return parser._p.after

mrs_header_tag_template = [
    r"browse .*?\r\n", # 0
    pexpect.EOF, # 2
    pexpect.TIMEOUT, # 3
]

mrs_header_tags = _compile_tag_template(mrs_header_tag_template)

mrs_header_actions = {
    0:_pass,
    1:_raise_exception,
    2:_raise_exception, # TODO: Something different
}

# Result actions
mrs_result_tag_template = [
    r"avm .*?\r\n", # 0
    r"LUI: unknown .*?\r\n", # 1
    r"LUI: out-of-date .*?\r\n", #2
    pexpect.EOF, # 3
    pexpect.TIMEOUT, # 4
]

mrs_result_actions = {
    0:_extract_mrs,
    1:_no_parse,
    2:_raise_exception,
    3:_no_parse,
    4:_raise_exception, # TODO: Something different
}

mrs_result_tags = _compile_tag_template(mrs_result_tag_template)


def receive_mrs(parser):
    # TODO: this
    """
    Use pexpect to receive text output of MRS from parser in LUI mode
    """
    header_ID = parser._p.expect(mrs_header_tags, timeout=1)
    ID = parser._p.expect(mrs_result_tags, timeout=1)
    response = mrs_result_actions[ID](parser)
    return response


## AVM commands
def receive_avm(parser):
    # TODO: this
    """
    Format:
        avm <avm_ID> #D[.*] "edge"
    """
    avm = ""
    return avm


# Pickle API
## Load commands
### Derivation commands
strip_quotes = re.compile("^[\'\"]|[\'\"]$")
legal_punctuation = re.escape("'’-+=/:.!?$<>@#%^&*")
lui_derivation_pattern = " ".join(("(?P<EDGE_ID>\d+)",
                                   "(?P<LABEL>{0}[\w{1}]+{0})",
                                   "(?P<TOKEN>({0}[\w{1}]+{0}|nil))",
                                   "(?P<CHART_ID>\d+)",
                                   "(?P<RULE_NAME>[\w{1}]+)",)).format("[\'\"]?", legal_punctuation)

def load_derivations(string):
    """
    Deserializes LUI tree string into PyDelphin Derivation objects

    Based on NLTK's Tree.fromstring()
    
    Format:
        (tree <tree_ID> #T[<edge_ID> "?<label>"? ("<token>"|nil) <chart_ID> <rule_name> (#T[.*])?] "<text>"\n\n)*

    """
    newlines = re.compile(r"\n{2,}")
    result = []
    for s in newlines.split(string):
        s = s.strip()
        # Parse introduction
        if s.startswith("tree "):
            _, tree_ID, s = s.split(None, 2)
            if s.endswith('"'): # Only do this if there's a quote at the end
                s = s.rsplit('"', 2)[0].strip() # assumes no quote in text
        else:
            tree_ID = None
        # Initialize bracket pointers        
        open_b = "#T["
        close_b = "]"
        open_pattern, close_pattern = (re.escape(open_b), re.escape(close_b))
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
            if token.startswith(open_b):
                if len(stack) == 1 and len(stack[0][1]) > 0:
                    _parse_error(s, match, 'end-of-string')
                edge_ID = match.group('EDGE_ID')
                label = match.group('LABEL')
                token = match.group('TOKEN')
                chart_ID = match.group('CHART_ID')
                rule_name = match.group('RULE_NAME')
                stack.append(((edge_ID, label, token, chart_ID, rule_name), []))
            # End of a tree/subtree
            elif token == close_b:
                if len(stack) == 1:
                    if len(stack[0][1]) == 0:
                        _parse_error(s, match, open_b)
                    else:
                        _parse_error(s, match, 'end-of-string')
                data, children = stack.pop()
                stack[-1][1].append(Derivation(None, data_package=data, children=children))
            # Leaf node
            else:
                if len(stack) == 1:
                    _parse_error(s, match, open_b)
                stack[-1][1].append(token)

        # check that we got exactly one complete tree.
        if len(stack) > 1:
            _parse_error(s, 'end-of-string', close_b)
        elif len(stack[0][1]) == 0:
            _parse_error(s, 'end-of-string', open_b)
        else:
            assert stack[0][0] is None
            assert len(stack[0][1]) == 1
        tree = stack[0][1][0]
            
        # Get tree ID
        tree.tree_ID = tree_ID
        result.append(tree)

    return result
    

def load_avm():
    # TODO: this
    """
    deserializes LUI AVM string into PyDelphin AVM object
    """
    pass

## MRS
_mrs_sorts = tuple("uipexh") # TODO: Get this from somewhere else?

def _validate_sort(sort, method_name="load_mrs"):
    if sort not in _mrs_sorts:
        raise ValueError("Sort value {!r} invalid at {}.{}()".format(sort, __name__, method_name))

### MRS Extraction methods
def _extract_mrs_avm(tokens, brackets="[]", keys=("TOP","LTOP","INDEX","RELS","XARG","ICONS","HCONS")):
    """
    Extract a dictionary of constituent tokens from a LUI-style MRS (AVM)
    
    Output (e.g.):
    {
        "TOP":{'value':[...], 'id': 0}
        "INDEX":{'value':[...], 'id': 0}
        "RELS":{'value':[...]}
        "HCONS":{'value':[...]}
    }

    kwargs:
        brackets: 
    """
    # Verify parameters
    if len(brackets) != 2:
        raise ValueError("{}._extract_mrs_avm() brackets parameter should be length of 2".format(__class__))
    if len(keys) < 1:
        raise ValueError("{}._extract_mrs_avm() keys parameter should be an iterable of length at least 1".format(__class__))
    # Extract AVM
    depth = 0
    entered = False
    start = 0
    open_b, close_b = brackets
    coref_open_b, coref_close_b = "<>" # TODO: change this?
    result = defaultdict(dict)
    current_key = None
    for i, token in enumerate(tokens):
        if token == open_b:
            depth += 1
            # Beginning of AVM
            if not entered and depth == 1:
                entered = True
            # Start new AVM
            elif depth == 2:
                if i <= 0:
                    raise ValueError("Something terribly bad happened at {}.load_mrs()".format(__name__))
                # Go back through the last couple values and find key
                for j in range(10):
                    if tokens[i-j+1] == coref_close_b: # tokens[i-j] if a coref
                        current_coref = tokens[i-j]
                        found_coref = True
                    if tokens[i-j] in keys:
                        current_key = tokens[i-j]
                        break
                start = i # keep track of start of AVM
                if current_key not in keys:
                    raise ValueError("MRS has unrecognized key {!r} at {}.load_mrs()".format(current_key, __name__))
        elif token == close_b:
            depth -= 1
            # End of AVM
            if not entered and depth == 0:
                raise ValueError("Expected a {open_b} but found a {close_b} at {name}.load_mrs()".format(open_b=open_b, close_b=close_b, name=__name__))
            elif entered and depth == 0: # done!
                break
            # Capture current structure to data set
            elif depth == 1: # was 2
                if not current_key:
                    raise ValueError("AVM closed without a valid key at {}.load_mrs()".format(__name__))
                result[current_key]["value"] = tokens[start:i+1]
                if found_coref:
                    result[current_key]["id"] = current_coref
            found_coref = False

    return dict(result) # Convert from defaultdict to dict

def _extract_avm_list(tokens):
    """
    Converts tokenized AVM-style recursive list to flat python list of AVMs.

    Note that this removes the null REST at the end. Therefore:
        len(input) == len(output)+1

    Format:
        [ *cons* FIRST : #D [ qeq HARG : < 0 > = #D [ h ] LARG : < 1 > = #D [ h ] ] REST : #D [ *cons* FIRST : #D [ qeq HARG : < 6 > = #D [ h ] LARG : < 4 > = #D [ h ] ] REST : #D [ *null* ] ] ] ]
    """
    first, rest = "FIRST", "REST"
    start = 0
    result = []
    for i, token in enumerate(tokens):
        if token == first:
            i3 = i+3
            if i3 <= len(tokens) and tokens[i3] == "[":
                start = i3-1 # Get the #D
            else:
                raise ValueError("{}._extract_avm_list() received an invalid AVM with FIRST not preceding an AVM (expected '[', found {} instead)".format(__name__, tokens[i3]))
        elif token == rest:
            result.append(tokens[start:i])
    return result


## Extract MRS components
def _extract_hook(result):
    top, index, xarg = None, None, None
    ## Get TOP
    key = "TOP" if "TOP" in result else "LTOP"
    if key in result:
        sort = result[key]["value"][1]
        _validate_sort(sort)
        top = MrsVariable(vid=result[key]["id"], sort=sort)
    ## Get INDEX
    key = "INDEX"
    if key in result:
        sort = result[key]["value"][1]
        _validate_sort(sort)
        index = MrsVariable(vid=result[key]["id"], sort=sort)
    ## Get XARG
    key = "XARG"
    if key in result:
        sort = result[key]["value"][1]
        _validate_sort(sort)
        xarg = MrsVariable(vid=result[key]["id"], sort=sort)
    ## Build Hook
    return Hook(top=top, index=index, xarg=xarg)

def _extract_rels(result_map):
    """
    Extract the relations from a given LUI string

    TODO: Break this into constituent functions
    """
    key = "RELS"
    distance_from_key_to_vid = 3
    distance_from_key_to_sort = 8
    distance_from_key_to_properties = 9
    distance_from_key_to_next = 10
    result = []
    if key in result_map:
        rels = _extract_avm_list(result_map[key]['value'])
        for rel in rels:
            # Validate relation
            if len(rel) < 3:
                raise ValueError("{}._extract_rels() given empty tokens")
            # Well-formed LUI #D structures will have their pred at position 2
            predicate = Pred.stringpred(rel[2])
            # Gather the rest of the values
            i = 3
            args = []
            while i < len(rel[3:])-1: # Nothing interesting exists at the last slot
                token = rel[i]
                if token == "LBL":
                    sort = rel[i+distance_from_key_to_sort]
                    _validate_sort(sort)
                    label = MrsVariable(vid=rel[i+distance_from_key_to_vid], sort=sort)
                    i += distance_from_key_to_next # Skip ahead
                elif token.startswith("ARG"):
                    # Get properties
                    properties = {}
                    search_space = rel[i+distance_from_key_to_properties:]
                    for j, item in enumerate(search_space): # 9 tokens before properties
                        if item == ":":
                            key = search_space[j-1]
                            value = search_space[j+1]
                            properties[key] = value
                        if item == "]":
                            break
                    # Build argument
                    sort = rel[i+distance_from_key_to_sort]
                    _validate_sort(sort)
                    argument = MrsVariable(vid=rel[i+distance_from_key_to_vid], sort=sort, properties=properties)
                    args.append(Argument.mrs_argument(token, argument))
                    i += distance_from_key_to_properties+j # Jump ahead!
                elif token in ("RSTR","BODY"):
                    sort = rel[i+distance_from_key_to_sort]
                    _validate_sort(sort)
                    args.append(Argument.mrs_argument(token, MrsVariable(vid=rel[i+distance_from_key_to_vid], sort=sort)))
                    i += distance_from_key_to_next
                elif rel[i+1] == ":": # If this is a key and it's not one of the above... freak out!
                    raise ValueError("{}._extract_rels() doesn't know what to do with key {}".format(__name__, token))
                else: # TODO: Do we actually want this?
                    i += 1
            # Validate predicate
            if not args or not label: # TODO: make better errors
                raise ValueError("{}._extract_rels() found an invalid elementary predication: {}".format(__name__, " ".join(rel)))
            # Build the predicate
            result.append(ElementaryPredication(predicate, label=label, args=args))
    return result

def _extract_hcons(result_map):
    key = "HCONS"
    result = []
    distance_from_key_to_tag = 3
    if key in result_map:
        values = _extract_avm_list(result_map[key]['value'])
        for handle in values:
            for i, token in enumerate(handle):
                if token == "HARG":
                    hiID = handle[i+distance_from_key_to_tag]
                elif token == "LARG":
                    loID = handle[i+distance_from_key_to_tag]
            hi = MrsVariable(vid=hiID, sort='h')
            lo = MrsVariable(vid=loID, sort='h')
            result.append(HandleConstraint.qeq(hi, lo))
    return result

def _extract_icons(result_map):
    return None

def load_mrs(mrs_string):
    # TODO: this
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

    tokens = avm_tokenize(mrs_string)
    result = _extract_mrs_avm(tokens)

    # Get HOOK
    hook = _extract_hook(result)
    # Get RELS
    rels = _extract_rels(result)
    # Get HCONS
    hcons = _extract_hcons(result)
    # Get ICONS (Planned feature)
    icons = _extract_icons(result)
    # Construct MRS
    return Mrs(hook=hook,
               rels=rels,
               hcons=hcons,
               icons=icons)


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
    Raise an error from load_derivations()

    From NLTK: http://www.nltk.org/_modules/nltk/tree.html
    """
    # Construct a basic error message
    if match == 'end-of-string':
        pos, token = len(s), 'end-of-string'
    else:
        pos, token = match.start(), match.group()
    msg = 'lui.load_derivations(): expected %r but got %r\n%sat index %d.' % (
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


