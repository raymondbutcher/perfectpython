"""
TODO:

* Add preferences
    * Define the pep8 MAX_LINE_LENGTH
    * Ignore specific error codes (is it possible to also do this via right-click?)

* Add some log messages / exception handling maybe

* Add pylint support
    * Add preferences for enabling/disabling pep8 and pylint
    * Check if built-in is also enabled, and complain

"""

import logging
import os
import re
import sys
import StringIO
import pep8
import tempfile

from pyflakes.scripts import pyflakes
from koLintResult import KoLintResult, SEV_ERROR, SEV_WARNING
from koLintResults import koLintResults
from xpcom import components


log = logging.getLogger("koPerfectPythonLinter")


class Checker(object):

    label = ''
    parse_pattern = None
    severity = SEV_WARNING

    def __init__(self, path, text):
        self.path = path
        self.text = text.splitlines(True)

    def add_to_results(self, results):
        for result in self.results():
            results.addResult(result)

    def parsed(self):
        for line in self.output.splitlines():
            match = self.parse_pattern.match(line)
            if match:
                yield match.groupdict()

    def results(self):

        for problem in self.parsed():

            line = int(problem['line'])
            column = int(problem.get('column', 1))

            description = ': '.join(part for part in (
                self.label,
                problem.get('code', ''),
                problem.get('description', ''),
            ) if part)

            line_text = self.text[line - 1]
            column_end = len(line_text)
            if column >= column_end:
                column = 1

            yield KoLintResult(
                description=description,
                severity=self.severity,
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
    severity = SEV_ERROR

    @property
    def output(self):
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


class koPerfectPython(object):

    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_clsid_ = "{e89c9a62-689d-2045-9210-24524bf8727c}"
    _reg_contractid_ = "@rbutcher.com/perfectpython;1"
    _reg_desc_ = "Perfect Python Komodo Extension"
    _reg_categories_ = [
        ("category-komodo-linter", 'Python'),
    ]

    checker_classes = (Pep8Checker, PyflakesChecker)

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

            for CheckerClass in self.checker_classes:
                checker = CheckerClass(temp_file.name, text)
                checker.add_to_results(results)

        finally:
            os.unlink(temp_file.name)

        return results
