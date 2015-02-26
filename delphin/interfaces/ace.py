
"""ACE interface"""

import re
import logging
import os
from subprocess import (check_call, CalledProcessError, Popen, PIPE, STDOUT)

# For InteractiveAce
import pexpect
from delphin.derivations.derivationtree import Derivation


class AceProcess(object):

    _cmdargs = []

    def __init__(self, grm, cmdargs=None, executable=None, **kwargs):
        if not os.path.isfile(grm):
            raise ValueError("Grammar file %s does not exist." % grm)
        self.grm = grm
        self.cmdargs = cmdargs or []
        self.executable = executable or 'ace'
        self._open()

    def _open(self):
        self._p = Popen(
            [self.executable, '-g', self.grm] +\
                self._cmdargs + self.cmdargs,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # don't try to handle any exceptions

    def send(self, datum):
        self._p.stdin.write(datum.rstrip() + '\n')
        self._p.stdin.flush()

    def receive(self):
        return self._p.stdout

    def interact(self, datum):
        self.send(datum)
        result = self.receive()
        return result

    def read_result(self, result):
        return result

    def close(self):
        self._p.stdin.close()
        for line in self._p.stdout:
            logging.debug('ACE cleanup: {}'.format(line.rstrip()))
        retval = self._p.wait()
        return retval

    def set_roots(roots):
        if isinstance(roots, str):
            self.cmdargs.extend(['r', roots])
        else:
            self.cmdargs.extend(['r'].extend(roots))


class AceParser(AceProcess):

    def receive(self):
        response = {
            'NOTES': [],
            'WARNINGS': [],
            'ERRORS': [],
            'SENT': None,
            'RESULTS': []
        }

        blank = 0

        stdout = self._p.stdout
        line = stdout.readline().rstrip()
        while True:
            if line.strip() == '':
                blank += 1
                if blank >= 2:
                    break
            elif line.startswith('SENT: ') or line.startswith('SKIP: '):
                response['SENT'] = line.split(': ', 1)[1]
            elif (line.startswith('NOTE:') or
                  line.startswith('WARNING') or
                  line.startswith('ERROR')):
                level, message = line.split(': ', 1)
                response['{}S'.format(level)].append(message)
            else:
                mrs, deriv = line.split(' ; ')
                response['RESULTS'].append({
                    'MRS': mrs.strip(),
                    'DERIV': deriv.strip()
                })
            line = stdout.readline().rstrip()
        return response


class AceGenerator(AceProcess):

    _cmdargs = ['-e']

    def receive(self):
        response = {
            'NOTE': None,
            'WARNING': None,
            'ERROR': None,
            'SENT': None,
            'RESULTS': None
        }
        results = []

        stdout = self._p.stdout
        line = stdout.read()
        while not line.startswith('NOTE: '):
            if line.startswith('WARNING') or line.startswith('ERROR'):
                level, message = line.split(': ', 1)
                response[level] = message
            else:
                results.append(line)
            line = stdout.readline().rstrip()
        # sometimes error messages aren't prefixed with ERROR
        if line.endswith('[0 results]') and len(results) > 0:
            response['ERROR'] = '\n'.join(results)
            results = []
        response['RESULTS'] = results
        return response


class InteractiveAce(AceProcess):
    """
    InteractiveAce class opens an instance of ACE in LUI mode
    to interact with ACE via the LUI.
    
    This overrides __exit__() to do nothing.
    Make sure to use close() when this is done!
    """

    def __init__(self, grm, cmdargs=None, executable=None):

        # CONDITIONS
        ## HEADER
        # 0: PARSE X -> Skip this line
        # 1: GROUP X -> Get the parse count (X)
        # 2: SKIP: -> no parses, return
        # 3: LUI: unknown X -> no parses, return
        # 4: <error> -> raise error
        # 5: timeout -> raise error
        ## PARSES
        # 0: tree X -> Get the tree ID, top node ID, load tree into data, get MRS
        # 1: LUI: unknown X -> no parses, return
        # 2: EOF -> n parses, return
        # 3: timeout -> raise error
        
        ace_parse_header_tags = [
            r"parse .*?\r\n", # 0
            r"group .*?\r\n", # 1
            r"SKIP: .*?\r\n", # 2
            r"LUI: unknown .*\r\n", # 3
            pexpect.EOF, # 4
            pexpect.TIMEOUT, # 5
        ]
        
        self.ace_header_actions = {
            0:self._pass,
            1:self._extract_parse_count,
            2:self._no_parse,
            3:self._no_parse,
            4:self._raise_exception,
            5:self._raise_exception, # TODO: Something different
        }

        self.ace_result_tags = [
            r"tree .*?\r\n", # 0
            r"LUI: unknown .*?\r\n", # 1
            pexpect.EOF, # 2
            pexpect.TIMEOUT, # 3
        ]

        self.ace_result_actions = {
            0:self._extract_parse,
            1:self._no_parse,
            2:self._no_parse,
            3:self._raise_exception, # TODO: Something different
        }

        self.ace_parse_header_tags = []
        for item in ace_parse_header_tags:
            if isinstance(item, str):
                self.ace_parse_header_tags.append(re.compile(item))
            else:
                self.ace_parse_header_tags.append(item)
                
        self.ace_header = re.compile(r"(parameter .*\r\n)*ACE: reading input from LUI\r\n")

        super().__init__(grm)

    def _pass(self, datum=""):
        pass
    
    def _open(self):

        command = [
            '-l',
            '--lui-fd=1',
            '--input-from-lui',
            '-g',
            self.grm,
        ] + self.cmdargs

        self._p = pexpect.spawnu(self.executable, command)
        self._p.maxread = 4096
        self._p.searchwindowsize = 10240
        
        self.ace_result_tags = self._p.compile_pattern_list(self.ace_result_tags)
        
        self._process_header()

        self.parse_count = {}

    def _process_header(self):
        """Header takes the form:

        parameter list-type *list*

        parameter empty-list-type *null*

        parameter non-empty-list-type *cons*

        parameter avm-collapsed-types [u i p e x h]

        ACE: reading input from LUI

        """

        self._p.expect(self.ace_header)

    def parse(self, datum):
        if not datum.strip():
            return {'SENT': "", 'RESULTS': []}
        self._send_parse(datum)
        return self._receive_parse(datum)

    def _send_parse(self, datum):
        self._p.sendline('parse %s' % datum.rstrip())

    def _receive_parse(self, datum):

        self.result = []
        self.blank = 0

        response = {
            'SENT': datum.strip('"'),
            'RESULTS': []
        }

        # Get parse count
        # TODO: Figure out what to do if ACE output malformed?
        self.parse_count[datum] = -1
        while self.parse_count[datum] < 0:
            ID = self._p.expect(self.ace_parse_header_tags)
            self.ace_header_actions[ID](datum=datum)

        # Get parses and create Derivations
        for i in range(self.parse_count[datum]):
            ID = self._p.expect(self.ace_result_tags, timeout=10)
            response['RESULTS'].append(Derivation(self.ace_result_actions[ID]()))

        # Get all of the reported parses
        # parses = []
        # for i in range(self.parse_count[datum]):
        #     #print("Getting parse {}".format(i))
        #     ID = self._p.expect(self.ace_result_tags, timeout=10)
        #     #print("BEFORE:", self._p.before)
        #     #print("MATCH:", self._p.match)
        #     #print("AFTER:", self._p.after)
        #     parses.append(self.ace_result_actions[ID]())

        # Get the MRS for each of the reported parses
        # for i in range(self.parse_count[datum]):
        #     #print("Getting mrs {}".format(i))
        #     deriv_ID = parses[i][1]
        #     deriv = parses[i][2].rsplit('"', 2)[0]
        #     top_edge_ID = deriv[len("#T["):].partition(' ')[0]
        #     # Get MRS
        #     mrs = self._request_mrs(deriv_ID, top_edge_ID)
        #     response['RESULTS'].append({
        #         'MRS': mrs.strip(),
        #         'DERIV': deriv.strip(),
        #     })

        return response

    def _extract_parse_count(self, datum=""):
        """
        Expected format: \group <count> "<text>"\
        """
        if not self.parse_count:
            self.parse_count = {}
        match = self._p.after.split(None, 2)
        if match[0] != "group":
            raise Exception("Something bad happened at InteractiveAce#_extract_parse_count()")
        text = match[2]
        if datum not in text:
            raise Exception("The parse input is not in the parse output at InteractiveAce#_extract_parse_count()")
        count = int(match[1])
        self.parse_count[datum] = count

    def _extract_parse(self):
        """
        Expected format: 
            \tree <tree_ID> #T[<edge_ID> "<label>" "<token>" <chart_ID> <rule_name> (#T[.*])?] "<text>"\
        """

        return self._p.after

    def _browse(self, tree_ID, edge_ID, what):
        #self._p.stdin.write('browse %s %s %s^L' % (tree_ID, edge_ID, what))
        #self._p.stdin.flush()
        self._p.sendline('browse %s %s %s' % (tree_ID, edge_ID, what))

    def _request_mrs(self, tree_ID, edge_ID):
        self._browse(tree_ID, edge_ID, "mrs simple")
        ID = -1
        while True:
            ID = self._p.expect(['browse .*\r\n', 'avm .*\r\n']) # relies on wxlui set up to cat STDOUT
            after = self._p.after.split('\n')
            lines = [line for line in after if line.startswith('avm')]
            if any(lines):
                mrs = lines[0]
                break
        # mrs == \avm <avm_ID> <MRS> "Simple MRS"\
        return mrs.split(None, 2)[2].rsplit('"', 2)[0]

    def _request_avm(self, tree_ID, edge_ID):
        self._browse(tree_ID, edge_ID, "avm")
        return self._p.readline().rstrip()

    def _no_parse(self, datum=""):
        return 0, "No parse found for {}.".format(datum)

    def _raise_exception(self, datum=""):
        exception = self._p.after
        raise exception(str(self._p))

    def close(self):
        self._p.sendline('^C')
        try:
            self._p.close()
        except:
            pass
        # Status will either be in 
        # exit status (if normal) or signalstatus (if abnormal)
        return self._p.exitstatus or self._p.signalstatus
    
    def __exit__(self, exc_type, exc_value, traceback):
        return False  # don't try to handle any exceptions

    def interact(self):
        """
        Don't use this!
        """
        raise Warning("InteractiveAce#interact() is not defined.")



def compile(cfg_path, out_path, log=None):
    #debug('Compiling grammar at {}'.format(abspath(cfg_path)), log)
    try:
        check_call(
            ['ace', '-g', cfg_path, '-G', out_path],
            stdout=log, stderr=log, close_fds=True
        )
    except (CalledProcessError, OSError):
        logging.error(
            'Failed to compile grammar with ACE. See {}'
            .format(abspath(log.name) if log is not None else '<stderr>')
        )
        raise
    #debug('Compiled grammar written to {}'.format(abspath(out_path)), log)


def parse_from_iterable(dat_file, data, **kwargs):
    with AceParser(dat_file, **kwargs) as parser:
        for datum in data:
            yield parser.interact(datum)


def parse(dat_file, datum, **kwargs):
    return next(parse_from_iterable(dat_file, [datum], **kwargs))


def generate_from_iterable(dat_file, data, **kwargs):
    with AceGenerator(dat_file, **kwargs) as generator:
        for datum in data:
            yield generator.interact(datum)


def generate(dat_file, datum, **kwargs):
    return next(generate_from_iterable(dat_file, [datum], **kwargs))


# def do(cmd):
#     # validate cmd here (e.g. that it has a 'grammar' key, correct 'task', etc)
#     task = cmd['task']
#     grammar = cmd['grammar']
#     cmdargs = cmd['arguments'] + ['-g', grammar]
#     if task == 'parse':
#         process_output = parse_results
#     elif task == 'transfer':
#         process_output = transfer_results
#     elif task == 'generate':
#         process_output = generation_results
#     else:
#         logging.error('Task "{}" is unsupported by the ACE interface.'
#                       .format(task))
#         return
#     cmdargs = map(lambda a: a.format(**cmd['variables']), cmdargs)
#     _do()
