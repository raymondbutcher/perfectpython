var koPrefset;
var widgets;
var defaultPreferences = {
    'pep8': {
        'enabled': true,
        'maxLineLength': 80
    },
    'pyflakes': {
        'enabled': false
    },
    'pylint': {
        'enabled': true
    }
}


var getPrefs = function() {
    
    function getOrCreate(name, defaultValue) {
        if (typeof(defaultValue) == 'boolean') {
            if (!koPrefset.hasPref(name)) {
                koPrefset.setBooleanPref(name, defaultValue);
                return defaultValue
            }
            return koPrefset.getBooleanPref(name);
        } else {
            if (!koPrefset.hasPref(name)) {
                koPrefset.setStringPref(name, defaultValue);
                return defaultValue
            }
            return koPrefset.getStringPref(name)
        }
    }
    
    return {
        'pep8': {
            'enabled': getOrCreate('perfectpython.pep8.enabled', defaultPreferences.pep8.enabled),
            'maxLineLength': getOrCreate('perfectpython.pep8.maxLineLength', defaultPreferences.pep8.maxLineLength)
        },
        'pyflakes': {
            'enabled': getOrCreate('perfectpython.pyflakes.enabled', defaultPreferences.pyflakes.enabled)
        },
        'pylint': {
            'enabled': getOrCreate('perfectpython.pylint.enabled', defaultPreferences.pylint.enabled)
        }
    }
    
}


function toggleWarnLineLength(from) {
    if (from == widgets.pep8.warnLineLength) {
        if (from.checked) {
            widgets.pep8.maxLineLength.value = '';
        } else {
            widgets.pep8.maxLineLength.value = defaultPreferences.pep8.maxLineLength
        }
    } else {
        widgets.pep8.warnLineLength.checked = Boolean(widgets.pep8.maxLineLength.value);
    }
}


function OnPreferencePageInitalize(prefset) {
    koPrefset = prefset;
    widgets = {
        'pep8': {
            'enabled': document.getElementById('perfectpython-pep8-enabled'),
            'warnLineLength': document.getElementById('perfectpython-pep8-warnLineLength'),
            'maxLineLength': document.getElementById('perfectpython-pep8-maxLineLength')
        },
        'pyflakes': {
            'enabled': document.getElementById('perfectpython-pyflakes-enabled')
        },
        'pylint': {
            'enabled': document.getElementById('perfectpython-pylint-enabled')
        }
    }
}


function OnPreferencePageLoading(prefset) {
    
    prefs = getPrefs()
    
    widgets.pep8.enabled.checked = prefs.pep8.enabled;
    widgets.pep8.maxLineLength.value = prefs.pep8.maxLineLength;
    toggleWarnLineLength(widgets.pep8.maxLineLength);
    
    widgets.pyflakes.enabled.checked = prefs.pyflakes.enabled;
    
    widgets.pylint.enabled.checked = prefs.pylint.enabled;
    
}
