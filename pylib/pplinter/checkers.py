import re
import sys
import StringIO

from koLintResult import KoLintResult, SEV_ERROR, SEV_WARNING
from pplinter.preferences import PrefSet


class Checker(object):

    column_offset = 0
    label = ''
    parse_pattern = None
    pref_scope = None

    def __init__(self, request, path, text):
        self.request = request
        self.path = path
        self.text = text.splitlines(True)

    def add_to_results(self, results):
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
            self._preferences = PrefSet(self.request, 'perfectpython.%s' % self.pref_scope)
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
        ids = []
        if not self.max_line_length:
            ids.append('E501')
        return ids

    @staticmethod
    def get_severity(code, description):
        return SEV_WARNING

    @property
    def max_line_length(self):
        if not hasattr(self, '_max_line_length'):
            try:
                number = int(self.preferences.get_or_create('maxLineLength', '80'))
            except ValueError:
                number = None
            self._max_line_length = number
        return self._max_line_length

    @property
    def output(self):

        if not self.preferences.get_or_create('enabled', True):
            return ''

        options = [self.path, '--repeat']

        ignored_ids = self.get_ignored_ids()
        options.extend(('--ignore', ','.join(ignored_ids) or 'none'))

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

        if not self.preferences.get_or_create('enabled', False):
            return ''

        stderr, sys.stderr = sys.stderr, StringIO.StringIO()
        stdout, sys.stdout = sys.stdout, StringIO.StringIO()
        try:

            from pyflakes.scripts import pyflakes
            pyflakes.checkPath(self.path)

            errors = sys.stderr.getvalue().strip()
            if errors:
                return errors
            else:
                return sys.stdout.getvalue().strip()

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

    @staticmethod
    def get_ignored_ids():
        return (
            'C0111',  # Missing docstring
            'C0301',  # Line too long
            'I0011',  # Locally disabling <message-id>
            'R0903',  # Too few public methods
            'R0921',  # Abstract class not referenced
            'W0201',  # Attribute defined outside __init__
            'W0232',  # Class has no __init__ method
            'W0613',  # Unused argument
            'W0703',  # Catching too general exception Exception
        )

    @property
    def output(self):

        if not self.preferences.get_or_create('enabled', True):
            return ''

        options = []
        options.extend(('--disable', ','.join(self.get_ignored_ids())))
        options.extend(('--include-ids', 'y'))
        options.extend(('--module-rgx', '.+'))  # Don't complain about the temp filename
        options.extend(('--reports', 'n'))
        options.append(self.path)

        stdout, sys.stdout = sys.stdout, StringIO.StringIO()
        try:

            from pylint import lint
            lint.Run(options, exit=False)
            return sys.stdout.getvalue().strip()

        finally:
            sys.stdout = stdout

    @staticmethod
    def get_severity(code, description):
        for code_type in ('E', 'F'):
            if code.startswith(code_type):
                return SEV_ERROR
        else:
            return SEV_WARNING
