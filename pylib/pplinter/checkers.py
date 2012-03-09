import koprocessutils
import logging
import os
import process
import re
import sys
import StringIO

from koLintResult import KoLintResult, SEV_ERROR, SEV_WARNING
from pplinter.preferences import PrefSet


LOG = logging.getLogger('perfectpython')


class Checker(object):

    column_offset = 0
    label = ''
    parse_pattern = None
    pref_scope = None

    def __init__(self, request, path, text_lines, python=None):
        self.request = request
        self.path = path
        self.text = text_lines
        self.python = python

    def add_to_results(self, results):
        if self.preferences.get_boolean('enabled'):
            for result in self.results():
                results.addResult(result)

    @staticmethod
    def get_severity(code, description):
        raise NotImplementedError()

    @property
    def output(self):
        raise NotImplementedError()

    def parsed(self):
        for line in self.output.splitlines():
            match = self.parse_pattern.match(line)
            if match:
                yield match.groupdict()

    @property
    def preferences(self):
        if not hasattr(self, '_preferences'):
            self._preferences = PrefSet(self.request, self.pref_scope)
        return self._preferences

    def results(self):

        for problem in self.parsed():

            line = int(problem['line'])
            column = int(problem.get('column', 1)) + self.column_offset
            code = problem.get('code', '')
            description = problem.get('description', '')

            severity = self.get_severity(code, description)

            message = ': '.join(part for part in (
                self.label,
                code,
                description,
            ) if part)

            line_text = self.text[line - 1]
            column_end = len(line_text)
            if column >= column_end:
                column = 1

            yield KoLintResult(
                description=message,
                severity=severity,
                lineStart=line,
                lineEnd=line,
                columnStart=column,
                columnEnd=column_end,
            )


class Pep8Checker(Checker):

    label = 'PEP8'
    parse_pattern = re.compile(r'^.+?:%s:%s:\s*%s\s*%s$' % (
        '(?P<line>\d+)',
        '(?P<column>\d+)',
        '(?P<code>[A-Z]\d+)',
        '(?P<description>.+)',
    ))
    pref_scope = 'pep8'

    def get_ignored_ids(self):
        if not self.max_line_length:
            return 'E501'
        return 'none'

    @staticmethod
    def get_severity(code, description):
        return SEV_WARNING

    @property
    def max_line_length(self):
        if not hasattr(self, '_max_line_length'):
            try:
                number = int(self.preferences.get_string('maxLineLength'))
            except ValueError:
                number = None
            self._max_line_length = number
        return self._max_line_length

    @property
    def output(self):

        options = [self.path, '--repeat']

        options.extend(('--ignore', self.get_ignored_ids()))

        stdout, sys.stdout = sys.stdout, StringIO.StringIO()
        try:

            import pep8
            pep8.MAX_LINE_LENGTH = self.max_line_length or 79
            pep8.process_options(options)
            pep8.input_file(self.path)
            return sys.stdout.getvalue().strip()

        finally:
            sys.stdout = stdout


class PyflakesChecker(Checker):

    label = 'Pyflakes'
    parse_pattern = re.compile(r'^.+?:(?P<line>\d+):\s*(?P<description>.+)$')
    pref_scope = 'pyflakes'

    @staticmethod
    def get_severity(code, description):
        warnings = (
            'imported but unused',
            'never used',
            'redefinition of function',
            'redefinition of unused',
        )
        for phrase in warnings:
            if phrase in description:
                return SEV_WARNING
        else:
            return SEV_ERROR

    @property
    def output(self):

        stderr, sys.stderr = sys.stderr, StringIO.StringIO()
        stdout, sys.stdout = sys.stdout, StringIO.StringIO()
        try:

            from pyflakes.scripts import pyflakes
            pyflakes.checkPath(self.path)

            errors = sys.stderr.getvalue().strip()
            if errors:
                return errors
            else:
                output = sys.stdout.getvalue().strip()
                return output

        finally:
            sys.stderr = stderr
            sys.stdout = stdout


class PylintChecker(Checker):

    label = 'Pylint'
    column_offset = 1
    parse_pattern = re.compile(r'^%s:\s*%s,%s:\s*%s' % (
        '(?P<code>[A-Z]\d+)',
        '(?P<line>\d+)',
        '(?P<column>\d+)',
        '(?P<description>.+)$',
    ))
    pref_scope = 'pylint'

    pylint_config_warning = 'No config file found, using default configuration\n'
    pylint_python_code = '''
import os
import sys
all_paths = []
all_paths += os.environ.get("KOMODO_PATHS_BEFORE").split(os.pathsep)
all_paths += sys.path
all_paths += os.environ.get("KOMODO_PATHS_AFTER").split(os.pathsep)
sys.path = []
for path in all_paths:
    if path not in sys.path:
        sys.path.append(path)
from pylint.lint import Run
Run(sys.argv[1:])
'''

    def get_ignored_ids(self):
        return self.preferences.get_string('ignoredIds')

    @staticmethod
    def get_severity(code, description):
        for code_type in ('E', 'F'):
            if code.startswith(code_type):
                return SEV_ERROR
        else:
            return SEV_WARNING

    @property
    def output(self):

        options = []
        options.extend(('--disable', self.get_ignored_ids()))
        options.extend(('--include-ids', 'y'))
        options.extend(('--good-names', '_,db'))
        options.extend(('--module-rgx', '.+'))  # Don't complain about the temp filename
        options.extend(('--reports', 'n'))
        options.append(self.path)

        if self.python:
            return self.run_externally(options)
        else:
            return self.run_internally(options)

    def run_externally(self, options):

        command = [self.python, '-c', self.pylint_python_code]

        environment = koprocessutils.getUserEnv()
        environment['KOMODO_PATHS_BEFORE'] = self.preferences.get_string('pythonExtraPaths', scope='')
        environment['KOMODO_PATHS_AFTER'] = os.pathsep.join(sys.path)

        pylint_process = process.ProcessOpen(
            cmd=command + options,
            cwd=self.request.cwd,
            env=environment,
            stdin=None,
        )
        stdout, stderr = pylint_process.communicate()
        if stderr != self.pylint_config_warning:
            LOG.critical('Error running pylint script: %s' % stderr)
            LOG.warn('Command: %s' % command)
            LOG.warn('Environment: %s' % environment)
            LOG.warn('Standard Output: %s' % stdout)
        return stdout.strip()

    @staticmethod
    def run_internally(options):
        """This is never used but I'll leave it here anyway."""

        stdout, sys.stdout = sys.stdout, StringIO.StringIO()
        try:

            from pylint import lint
            lint.Run(options, exit=False)
            return sys.stdout.getvalue().strip()

        finally:
            sys.stdout = stdout
