

class TypedFeatureStructure(object):
    """
    TypedFeatureStructure stores DELPH-IN-style Typed Feature Structures (TFS),
    which consist primarily of a type and an Attribute Value Matrix (AVM).
    A TFS is technically an Directed Acylic Graph (DAG).

    Each TypedFeatureStructure object also has a coreference ID, which
    represents the TFS' identity with another TFS. Each value of an AVM
    is either a string or a TypedFeatureStructure object, and therefore
    TypedFeatureStructure objects are stored as trees. The combination
    of this tree-structure and the coreferences create the DAG structure.

    Optionally TypedFeatureStructure objects contain an
    AVM_ID, which is typically a processor-internal unique ID.

    Author: Michael Goodman, T.J. Trimble
    """

    __slots__ = ['_type', '_avm', '_coref', '_avm_ID']

    def __init__(self, type=None, featvals=None, coref=None):
        self._type = str(type) if type else None
        try:
            self._coref = int(coref) if coref else None
        except ValueError:
            raise ValueError("TypedFeatureStructure coref must be an int")
        self._avm = {}
        if isinstance(featvals, dict):
            featvals = featvals.items()
        for feat, val in list(featvals or []):
            self[feat] = val

    def __repr__(self):
        return '<TypedFeatureStructure object ({}{}) at {}>'.format(
            self._type,
            "_{}".format(self._coref) if self._coref else "",
            id(self)
        )

    def __str__(self):
        values = "\n".join(line for line in sorted(": ".join(map(str, path)) for path in self.features()))
        pieces = {
            "VALUES": ":\n{}".format(values) if values else "",
            "COREF": "[{}] ".format(self._coref) if self._coref else "",
            "TYPE": self.type if self._is_notable and self._type else "",
        }
        return "{COREF}{TYPE}{VALUES}".format(**pieces)

    def __setitem__(self, key, val):
        try:
            first, rest = key.split('.', 1)
        except ValueError:
            self._avm[key.upper()] = val
        else:
            first = first.upper()  # features are case-insensitive
            try:
                subdef = self._avm[first]
            except KeyError:
                # use type(self) so it still works with inherited classes
                subdef = self._avm.setdefault(first, type(self)())
            subdef[rest] = val

    def __getitem__(self, key):
        try:
            first, rest = key.split('.', 1)
        except ValueError:
            return self._avm[key.upper()]
        else:
            return self._avm[first.upper()][rest]

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, value):
        self._type = value

    @property
    def coref(self):
        return self._coref

    @property
    def avm_ID(self):
        return self._avm_ID
    @avm_ID.setter
    def avm_ID(self, value):
        self._avm_ID = value


    def get(self, key, default=None):
        try:
            val = self[key]
        except KeyError:
            return default

    def _is_notable(self):
        """
        Notability determines if the TFS should be listed as the value
        of a feature or if the feature should just "pass through" its
        avm to get the next value. A notable TypedFeatureStructure is
        one without any other features (i.e. an empty AVM)
        """
        return not self._avm

    def features(self):
        for feat, val in self._avm.items():
            try:
                if val._is_notable():
                    yield (feat, val)
                else:
                    for subfeat, subval in val.features():
                        yield ('{}.{}'.format(feat, subfeat), subval)
            except AttributeError:
                yield (feat, val)

    def __eq__(self, other):
        import sys
        if not isinstance(other, self.__class__):
            print("Not same class", file=sys.stderr)
            print("self: ({}){}; other: ({}){}".format(self.__class__, self, other.__class__, other), file=sys.stderr)
            return False
        try:
            if self._type != other._type:
                print("Not same _type", file=sys.stderr)
                print("self: {}; other: {}".format(self._type, other._type), file=sys.stderr)
                return False
        except AttributeError:
            print("Not same _type", file=sys.stderr)
            return False
        try:
            if self._coref != other._coref:
                print("Not same _coref", file=sys.stderr)
                print("self: {}; other: {}".format(self._coref, other._coref), file=sys.stderr)
                return False
        except AttributeError:
            print("Not same _coref", file=sys.stderr)
            print("self: {}; other: {}".format(self._coref, other._coref), file=sys.stderr)
            return False
        try:
            if self._avm != other._avm:
                sim_keys = self._avm.keys() & other._avm.keys()
                #print("Similar keys: " + str(sim_keys), file=sys.stderr)
                #print("Not same _avm", file=sys.stderr)
                print("self.avm: " + str(self._avm), file=sys.stderr)
                print("self.avm.keys(): " + str(self._avm.keys() - sim_keys), file=sys.stderr)
                print("\n\n", file=sys.stderr)
                print("other.avm: " + str(other._avm), file=sys.stderr)
                print("other.avm.keys(): " + str(other._avm.keys() - sim_keys), file=sys.stderr)
                return False
        except AttributeError:
            print("Not same _avm", file=sys.stderr)
            return False
        return True


    def __ne__(self, other):
        return not __eq__(self, other)
            

    def __hash__(self):
        return hash(tuple(self._type, self._avm_ID, self._coref, self._avm))
