from koLintResult import getProxiedEffectivePrefs

SCOPE = 'perfectpython'

DEFAULTS = {
    'pep8': {
        'enabled': True,
        'maxLineLength': 80,
    },
    'pyflakes': {
        'enabled': False,
    },
    'pylint': {
        'enabled': True,
        'ignoredIds': 'C0111,C0301,I0011,R0903,R0921,W0201,W0232,W0613,W0703',
    }
}


class PrefSet(object):

    def __init__(self, request, scope):
        self.prefset = getProxiedEffectivePrefs(request)
        self.scope = scope

    def get_or_create(self, name, default=None):

        full_name = '%s.%s.%s' % (SCOPE, self.scope, name)

        if default is None:
            default = DEFAULTS[self.scope][name]

        if isinstance(default, bool):
            get_pref = self.prefset.getBooleanPref
            set_pref = self.prefset.setBooleanPref
        else:
            get_pref = self.prefset.getStringPref
            set_pref = self.prefset.setStringPref

        try:
            return get_pref(full_name)
        except Exception:
            set_pref(full_name, default)
            return default
