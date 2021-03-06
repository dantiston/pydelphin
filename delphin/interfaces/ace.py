
"""ACE interface"""

import logging
import os
from subprocess import (check_call, CalledProcessError, Popen, PIPE, STDOUT)

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
            [self.executable, '-g', self.grm] + self._cmdargs + self.cmdargs,
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
        line = stdout.readline().rstrip()
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
