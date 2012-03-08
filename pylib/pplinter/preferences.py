import logging

from koLintResult import getProxiedEffectivePrefs


LOG = logging.getLogger('perfectpython')

SCOPE = 'perfectpython'


class PrefSet(object):

    def __init__(self, request, scope):
        self.prefset = getProxiedEffectivePrefs(request)
        self.scope = scope

    def _get_full_name(self, name):
        return '%s.%s.%s' % (SCOPE, self.scope, name)

    def _get_preference(self, get_pref, name, scope):
        if scope is None:
            full_name = self._get_full_name(name)
        else:
            full_name = '.'.join(part for part in (scope, name) if part)
        try:
            return get_pref(full_name)
        except Exception:
            LOG.critical('Could not get preference: %s' % full_name)
            raise

    def get_boolean(self, name, scope=None):
        return self._get_preference(self.prefset.getBooleanPref, name, scope)

    def get_string(self, name, scope=None):
        return self._get_preference(self.prefset.getStringPref, name, scope)
