"""
Planned features:

* Pep8
    * Ignore specific codes

* Pylint
    * Ignore specific codes
    * Same max line length option as pep8

"""

import logging
import os
import tempfile

from koLintResults import koLintResults
from pplinter.checkers import Pep8Checker, PyflakesChecker, PylintChecker
from xpcom import components


LOG = logging.getLogger("perfectpython")


class PerfectPythonLinter(object):

    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_clsid_ = "{e89c9a62-689d-2045-9210-24524bf8727c}"
    _reg_contractid_ = "@rbutcher.com/perfectpython;1"
    _reg_desc_ = "Perfect Python Komodo Extension"
    _reg_categories_ = [
        ("category-komodo-linter", 'Python'),
    ]

    checker_classes = (Pep8Checker, PyflakesChecker, PylintChecker)

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

            for checker_class in self.checker_classes:

                try:

                    checker = checker_class(request, temp_file.name, text)
                    checker.add_to_results(results)

                except Exception:
                    LOG.exception('Error running %s' % checker_class.__name__)

        finally:
            os.unlink(temp_file.name)

        return results
