import re

class Derivation(object):
    """
    A class for reading, writing, and storing derivation tree objects.

    @author: T.J. Trimble
    """

    legal_punctuation = re.escape("'’-+=/:.!?$<>@#%^&*")
    strip_quotes = re.compile("^[\'\"]|[\'\"]$")
    ace_pattern = " ".join(("(?P<EDGE_ID>\d+)",
                            "(?P<LABEL>{0}[\w{1}]+{0})",
                            "(?P<TOKEN>({0}[\w{1}]+{0}|nil))",
                            "(?P<CHART_ID>\d+)",
                            "(?P<RULE_NAME>[\w{1}]+)",)).format("[\'\"]?", legal_punctuation)

    def __init__(self, definition, data_package=None, children=None):
        """
        Two constructors:
            Derivation(str:definition):
                Construct a Derivation object from a bracketed tree structure from ACE.
                ex. Derivation("#T[<EDGE_ID> "<LABEL>" "<TOKEN>"|nil >CHART_ID> <RULE_NAME> <CHILDREN>]")

            Derivation(None, tuple:data_package, list:children):
                Construct a Derivation object from tuple of values and a list of children.
                The contents of data_package are:
                    edge_ID, label, token, chart_ID, rule_name, [tree_ID]
                ex. Derivation(None, data_package=(...), children=[])
        """
        if definition:
            tree = Derivation.read_ACE(definition)
            data_package = (tree.edge_ID, tree.label, tree.token, tree.chart_ID, tree.rule_name, tree.tree_ID)
            children = tree.children
        if children is None:
            raise TypeError("%s: Expected a node value and child list "
                            % type(self).__name__)
        elif isinstance(children, str):
            raise TypeError("%s() argument 2 should be a list, not a "
                            "string" % type(self).__name__)
        else:
            if len(data_package) not in (5, 6):
                raise ValueError("%s() data_package argument must be a "
                                 "tuple of length 5" % self.__class__.__name__)
        try:
            self.children = children
            self.edge_ID = data_package[0]
            self.label = Derivation.strip_quotes.sub("", data_package[1])
            self.token = Derivation.strip_quotes.sub("", data_package[2]) if data_package[2] not in (None, "nil") else None
            self.chart_ID = data_package[3]
            self.rule_name = data_package[4]
            self.tree_ID = data_package[5] if len(data_package) >= 6 else None
        except Exception as e:
            print("{} data_package at failue is {}".format(self.__class__.__name__, data_package))
            raise e
                
    # Interface specific methods
    #  Maybe move these to their respective interface classes?

    @classmethod
    def read_ACE(cls, s):
        """
        Based on NLTK's Tree.fromstring()

        Input Format:
            tree 1 #T[1 'S' nil 3 subj-head #T[2 'N' 'I' 93 i] #T[2 'V' 'run' 93 run_v1]] "I run"
        """
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
            open_pattern, Derivation.ace_pattern, close_pattern, valid_chars))
        # Walk through each token, updating a stack of trees.
        stack = [(None, [])] # list of (node, children) tuples
        tokens = list(token_re.finditer(s))
        for i, match in enumerate(tokens):
            token = match.group()
            # Definition of a tree/subtree
            #  #T[EDGE_ID LABEL TOKEN CHART_ID RULE_NAME
            if token.startswith(open_b):
                if len(stack) == 1 and len(stack[0][1]) > 0:
                    cls._parse_error(s, match, 'end-of-string')
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
                        cls._parse_error(s, match, open_b)
                    else:
                        cls._parse_error(s, match, 'end-of-string')
                data, children = stack.pop()
                stack[-1][1].append(cls(None, data_package=data, children=children))
            # Leaf node
            else:
                if len(stack) == 1:
                    cls._parse_error(s, match, open_b)
                stack[-1][1].append(token)

        # check that we got exactly one complete tree.
        if len(stack) > 1:
            cls._parse_error(s, 'end-of-string', close_b)
        elif len(stack[0][1]) == 0:
            cls._parse_error(s, 'end-of-string', open_b)
        else:
            assert stack[0][0] is None
            assert len(stack[0][1]) == 1
        tree = stack[0][1][0]

        # Get tree ID
        tree.tree_ID = tree_ID
        # return the tree
        return tree

    @classmethod
    def _parse_error(cls, s, match, expecting):
        """
        From NLTK: http://www.nltk.org/_modules/nltk/tree.html
        """
        # Construct a basic error message
        if match == 'end-of-string':
            pos, token = len(s), 'end-of-string'
        else:
            pos, token = match.start(), match.group()
        msg = '%s.read(): expected %r but got %r\n%sat index %d.' % (
            cls.__name__, expecting, token, ' '*12, pos)
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


    # Core methods
    def __eq__(self, other):
        """
        Two trees are equal if their labels, tokens, rule names, and 
        structures are the same. Edge IDs and chart IDs are irrelevant.
        """
        if not isinstance(other, Derivation):
            return False
        # Check attributes
        if self.label != other.label:
            return False
        if self.token != other.token:
            return False
        if self.rule_name != other.rule_name:
            return False
        ## Check children
        if len(self.children) != len(other.children):
            return False
        for i in range(len(self.children)):
            if self.children[i] != other.children[i]:
                return False
        # Return true if they're the same!
        return True

    ## Output methods
    # Standard methods
    def _output(self, format_string="[{LABEL}{TOKEN}{RULE}{CHILDREN}]"):
        format_map = {
            "EDGE_ID": " "+self.edge_ID,
            "LABEL": " "+self.label if self.label else "XP",
            "TOKEN": " "+self.token if self.token else "",
            "CHART_ID": " "+self.chart_ID,
            "RULE": " "+self.rule_name if self.rule_name else "",
            "CHILDREN": " {}".format(" ".join(child._output(format_string=format_string) for child in self.children)) if self.children else "",
        }
        return format_string.format(**format_map)

    def __str__(self):
        return self._output()


    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, str(self))


    # Pickle Methods
    def read(self):
        pass

    def reads(self):
        pass

    def dump(self):
        pass

    def dumps(self):
        pass
