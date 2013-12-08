import logging
import os
import re
import sys
import tempfile

from koLintResults import koLintResults
from pplinter.checkers import Pep8Checker, PyflakesChecker, PylintChecker
from xpcom import components


LOG = logging.getLogger('perfectpython')
#LOG.setLevel(logging.DEBUG)


class PerfectPythonLinter(object):

    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_clsid_ = '{e89c9a62-689d-2045-9210-24524bf8727c}'
    _reg_contractid_ = '@rbutcher.com/perfectpython;1'
    _reg_desc_ = 'Perfect Python Komodo Extension'
    _reg_categories_ = [
        ('category-komodo-linter', 'Python'),
    ]

    checker_classes = (Pep8Checker, PyflakesChecker, PylintChecker)

    def __init__(self):
        self._python = (
            components
            .classes['@activestate.com/koAppInfoEx?app=Python;1']
            .createInstance(components.interfaces.koIAppInfoEx)
        )

    def lint(self, request):
        text = request.content.encode(request.encoding.python_encoding_name)
        results = self.lint_with_text(request, text)
        return results

    def lint_with_text(self, request, text):

        if not text:
            return

        # Make the user's configured version of python available to the
        # checkers. They can start this exe in a new process or just
        # use the current interpreter.
        python = self._python.getExecutableFromDocument(request.koDoc)

        # Add the current dir so that the checkers can find relative files.
        if request.cwd not in sys.path:
            sys.path.append(request.cwd)

        # Avoid issues with windows newlines by pretending they don't exist.
        text = re.sub(r'\r\n', r'\n', text)

        text_lines = text.splitlines(True)

        results = koLintResults()

        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
        )

        try:

            temp_file.write(text)
            temp_file.close()

            for checker_class in self.checker_classes:

                try:

                    checker = checker_class(request, temp_file.name, text_lines, python=python)
                    checker.add_to_results(results)

                except Exception:
                    LOG.exception('Error running %s' % checker_class.__name__)

        finally:
            os.unlink(temp_file.name)
