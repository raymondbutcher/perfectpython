var koPrefset;
var widgets;
var defautPreferences = {
    'pep8': {
        'enabled': true,
        'maxLineLength': 80
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
            'enabled': getOrCreate('perfectpython.pep8.enabled', defautPreferences.pep8.enabled),
            'maxLineLength': getOrCreate('perfectpython.pep8.maxLineLength', defautPreferences.pep8.maxLineLength)
        }
    }
    
}


function toggleWarnLineLength(from) {
    if (from == widgets.pep8.warnLineLength) {
        if (from.checked) {
            widgets.pep8.maxLineLength.value = '';
        } else {
            widgets.pep8.maxLineLength.value = defautPreferences.pep8.maxLineLength
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
        }
    }
}


function OnPreferencePageLoading(prefset) {
    prefs = getPrefs()
    widgets.pep8.enabled.checked = prefs.pep8.enabled;
    widgets.pep8.maxLineLength.value = prefs.pep8.maxLineLength;
    toggleWarnLineLength(widgets.pep8.maxLineLength);
    
}





//
//
//function OnPreferencePageClosing(prefset, ok) {
//    if (!ok) return;
//}
//
//
//function OnPreferencePageOK(prefset) {
//    alert('ok');
//    return true;
//}


