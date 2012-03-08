import logging

from koLintResult import getProxiedEffectivePrefs


LOG = logging.getLogger("perfectpython")

SCOPE = 'perfectpython'


class PrefSet(object):

    def __init__(self, request, scope):
        self.prefset = getProxiedEffectivePrefs(request)
        self.scope = scope

    def _get_full_name(self, name):
        return '%s.%s.%s' % (SCOPE, self.scope, name)

    def _get_preference(self, get_pref, name):
        full_name = self._get_full_name(name)
        try:
            return get_pref(full_name)
        except Exception:
            LOG.critical('Could not get preference: %s' % full_name)
            raise

    def get_boolean(self, name):
        return self._get_preference(self.prefset.getBooleanPref, name)

    def get_string(self, name):
        return self._get_preference(self.prefset.getStringPref, name)
