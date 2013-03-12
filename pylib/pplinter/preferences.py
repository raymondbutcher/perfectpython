import logging

try:
    from koLintResult import getProxiedEffectivePrefs
    haveKO8 = False
except ImportError:
    # KO8
    haveKO8 = True


LOG = logging.getLogger('perfectpython')

# Ensure that this matches preferences.js and has no '.' characters in it.
SCOPE = 'pplint-0-6-5'

DEFAULTS = {
    SCOPE: {
        'pep8': {
            'enabled': True,
            'maxLineLength': '120',
        }
    }
}


class PrefSet(object):

    def __init__(self, request, scope):
        if haveKO8:
            self.prefset = request.prefset
        else:
            self.prefset = getProxiedEffectivePrefs(request)
        self.scope = scope

    def _get_preference(self, getter, name, scope):

        if scope is None:
            full_name = '.'.join((SCOPE, self.scope, name))
        else:
            full_name = '.'.join(part for part in (scope, name) if part)

        try:

            if self.prefset.hasPref(full_name):

                value = getter(full_name)
                LOG.debug('GOT PREFERENCE: %s = %s' % (full_name, value))

            else:

                value = DEFAULTS
                parts = full_name.split('.')
                while value and parts:
                    value = value.get(parts.pop(0))

                LOG.debug('USING DEFAULT PREFERENCE: %s = %s' % (full_name, value))

            return value

        except Exception:
            LOG.critical('ERROR GETTING PREFERENCE: %s' % full_name)
            raise

    def get_boolean(self, name, scope=None):
        getter = self.prefset.getBooleanPref
        return self._get_preference(getter, name, scope)

    def get_string(self, name, scope=None):
        getter = self.prefset.getStringPref
        return self._get_preference(getter, name, scope)
