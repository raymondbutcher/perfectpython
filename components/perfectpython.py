"""
Planned features:

* Add preferences
    * Define the MAX_LINE_LENGTH
    * Ignore specific error codes (is it possible to also do this via right-click?)
    * Enable or disable each checker
        * See if syntax checking is enabled
        * See if each built-in checker is enabled

* Add some log messages / exception handling maybe

"""

import logging
import os
import re
import sys
import StringIO
import tempfile

from koLintResult import KoLintResult, SEV_ERROR, SEV_WARNING
from koLintResults import koLintResults
from xpcom import components


LOG = logging.getLogger("koPerfectPythonLinter")


class Checker(object):

    column_offset = 0
    label = ''
    parse_pattern = None

    def __init__(self, path, text):
        self.path = path
        self.text = text.splitlines(True)

    def add_to_results(self, results):
        for result in self.results():
            results.addResult(result)

    @staticmethod
    def get_severity(text):
        return SEV_WARNING

    @property
    def output(self):
        raise NotImplementedError()

    def parsed(self):
        for line in self.output.splitlines():
            match = self.parse_pattern.match(line)
            if match:
                yield match.groupdict()

    def results(self):

        for problem in self.parsed():

            line = int(problem['line'])
            column = int(problem.get('column', 1)) + self.column_offset

            code = problem.get('code', '')

            description = ': '.join(part for part in (
                self.label,
                code,
                problem.get('description', ''),
            ) if part)

            severity = self.get_severity(code)

            line_text = self.text[line - 1]
            column_end = len(line_text)
            if column >= column_end:
                column = 1

            yield KoLintResult(
                description=description,
                severity=severity,
                lineStart=line,
                lineEnd=line,
                columnStart=column,
                columnEnd=column_end,
            )


class Pep8Checker(Checker):

    label = 'PEP8'
    parse_pattern = re.compile(r'^.+?:(?P<line>\d+):(?P<column>\d+):\s*(?P<code>[A-Z]\d+)\s*(?P<description>.+)$')

    @property
    def output(self):

        import pep8

        # Change some settings, but remember the original values.
        max_line_length, pep8.MAX_LINE_LENGTH = pep8.MAX_LINE_LENGTH, 120
        stdout, sys.stdout = sys.stdout, StringIO.StringIO()

        try:

            pep8.process_options([self.path, '--repeat', '--ignore', 'none'])
            pep8.input_file(self.path)
            return sys.stdout.getvalue().strip()

        finally:

            # Restore the original settings.
            pep8.MAX_LINE_LENGTH = max_line_length
            sys.stdout = stdout


class PyflakesChecker(Checker):

    label = 'Pyflakes'
    parse_pattern = re.compile(r'^.+?:(?P<line>\d+):\s*(?P<description>.+)$')

    @staticmethod
    def get_severity(text):
        return SEV_ERROR

    @property
    def output(self):

        from pyflakes.scripts import pyflakes

        stderr, sys.stderr = sys.stderr, StringIO.StringIO()
        stdout, sys.stdout = sys.stdout, StringIO.StringIO()
        try:

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
    parse_pattern = re.compile(r'^(?P<code>[A-Z]\d+):\s*(?P<line>\d+),(?P<column>\d+):\s*(?P<description>.+)$')

    @staticmethod
    def get_ignored_ids():
        return (
            #'C0103',  # Invalid name
            'C0111',  # Missing docstring
            'C0301',  # Line too long
            'I0011',  # Locally disabling <message-id>
            'W0703',  # Catching too general exception Exception
        )

    @property
    def output(self):

        from pylint import lint

        options = []
        options.extend(('--disable', ','.join(self.get_ignored_ids())))
        options.extend(('--include-ids', 'y'))
        options.extend(('--module-rgx', '.+'))  # Don't complain about the temp filename
        options.extend(('--reports', 'n'))
        options.append(self.path)

        stdout, sys.stdout = sys.stdout, StringIO.StringIO()
        try:

            lint.Run(options, exit=False)
            return sys.stdout.getvalue().strip()

        finally:
            sys.stdout = stdout

    @staticmethod
    def get_severity(text):
        for code in ('E', 'F'):
            if text.startswith(code):
                return SEV_ERROR
        else:
            return SEV_WARNING


class PerfectPython(object):

    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_clsid_ = "{e89c9a62-689d-2045-9210-24524bf8727c}"
    _reg_contractid_ = "@rbutcher.com/perfectpython;1"
    _reg_desc_ = "Perfect Python Komodo Extension"
    _reg_categories_ = [
        ("category-komodo-linter", 'Python'),
    ]

    @staticmethod
    def get_checker_classes():
        # Don't bother with PyflakesChecker because Pylint does everything.
        # When there are user preferences, then it might be good to let people
        # choose pyflakes instead of pylint.
        return (Pep8Checker, PylintChecker)

    def lint(self, request):
        text = request.content.encode(request.encoding.python_encoding_name)
        return self.lint_with_text(request, text)

    def lint_with_text(self, request, text):

        if not text:
            return

        results = koLintResults()

        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
        )

        try:

            temp_file.write(text)
            temp_file.close()

            for checker_class in self.get_checker_classes():

                try:

                    checker = checker_class(temp_file.name, text)
                    checker.add_to_results(results)

                except Exception:
                    LOG.exception('Error running %s' % checker_class.__name__)

        finally:
            os.unlink(temp_file.name)

        return results
