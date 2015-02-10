

class Parse(object):
    """
    Parse is an object storing the results of a parse result from
    an DELPH-IN interface
    """

    def __init__(self, results):
        self.text = results['SENT']
        self.note = results['NOTE']
        self.warning = results['WARNING']
        self.error = results['ERROR']
        self.results = results['RESULTS']
    
    @property
    def get_mrs(self):
        for i in range(len(self.results)):
            yield self.results[i]['MRS']

    @property
    def get_trees(self):
        for i in range(len(self.results)):
            yield self.results[i]['DERIV']
