from koLintResult import getProxiedEffectivePrefs


class PrefSet(object):

    def __init__(self, request, scope):
        self.prefset = getProxiedEffectivePrefs(request)
        self.scope = scope

    def get_or_create(self, name, default):

        full_name = '%s.%s' % (self.scope, name)

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
