// Ensure this matches preferences.py
var prefScope = 'pplint-0-6-5';

// Store the widget elements here.
var widgets;

// All preferences and their defaults.
// A value of undefined will allow a widget to be mapped,
// without actually linking to a preference.
var preferences = {
    'pep8': {
        'enabled': true,
        'warnLineLength': undefined,
        'maxLineLength': '120'
    },
    'pyflakes': {
        'enabled': false
    },
    'pylint': {
        'enabled': false,
        'ignoredIds': 'C0111,C0301,C0322,C0324,I0011,R0902,R0903,R0904,R0921,W0142,W0201,W0212,W0232,W0613,W0703'
    }
}


var getPrefs = function(prefset) {
    function getOrCreate(name, defaultValue) {
        if (typeof(defaultValue) == 'boolean') {
            if (prefset.hasPref(name)) {
                return prefset.getBooleanPref(name);
            } else {
                prefset.setBooleanPref(name, defaultValue);
                return defaultValue;
            }
        } else {
            if (prefset.hasPref(name)) {
                return prefset.getStringPref(name);
            } else {
                prefset.setStringPref(name, defaultValue);
                return defaultValue;
            }
        }
    }
    var results = {}
    for (type in preferences) {
        results[type] = {}
        for (name in preferences[type]) {
            var defaultValue = preferences[type][name];
            if (defaultValue != undefined) {
                var full_name = prefScope + '.' + type + '.' + name;
                try {
                    results[type][name] = getOrCreate(full_name, defaultValue);
                } catch (error) {
                    alert(error);
                }
            }
        }
    }
    return results;
}


var getWidgets = function() {
    var results = {}
    for (type in preferences) {
        results[type] = {}
        for (name in preferences[type]) {
            var id = 'perfectpython-' + type + '-' + name;
            results[type][name] = document.getElementById(id);
        }
    }
    return results;
}


function toggleWarnLineLength(from) {
    if (from == widgets.pep8.warnLineLength) {
        if (from.checked) {
            widgets.pep8.maxLineLength.value = preferences.pep8.maxLineLength;
        } else {
            if (parseInt(widgets.pep8.maxLineLength.value)) {
                preferences.pep8.maxLineLength = widgets.pep8.maxLineLength.value;
            }
            widgets.pep8.maxLineLength.value = '0';
        }
    } else {
        widgets.pep8.warnLineLength.checked = Boolean(parseInt(widgets.pep8.maxLineLength.value));
    }
}


function toggleDisabled(from) {
    for (name in widgets) {
        var scope = widgets[name];
        for (name in scope) {
            var widget = scope[name];
            if (from == widget) {
                for (index in scope) {
                    widget = scope[index];
                    if (from != widget) {
                        if (from.checked) {
                            if (widget.hasAttribute('disabled')) {
                                widget.removeAttribute('disabled');
                            }
                        } else {
                            widget.setAttribute('disabled', true);
                        }
                    }
                }
                return true;
            }
        }
    }
    return false;
}


function OnPreferencePageLoading(prefset) {
    
    try {
        
        if (!widgets) {
            widgets = getWidgets();
        }
        
        var prefs = getPrefs(prefset);
        
        // Set up Pep8 widgets.
        widgets.pep8.enabled.checked = prefs.pep8.enabled;
        widgets.pep8.maxLineLength.value = prefs.pep8.maxLineLength;
        toggleWarnLineLength(widgets.pep8.maxLineLength);
        
        // Set up Pyflakes widget.
        widgets.pyflakes.enabled.checked = prefs.pyflakes.enabled;
        
        // Set up Pylint widgets.
        widgets.pylint.enabled.checked = prefs.pylint.enabled;
        widgets.pylint.ignoredIds.value = prefs.pylint.ignoredIds;
        
        // Disable widgets if their checker is disabled.
        for (scope in widgets) {
            toggleDisabled(widgets[scope].enabled)
        }
        
    } catch(error) {
        alert(error);
    }
    
}


function OnPreferencePageOK(prefset) {
    try {
        
        for (checker in widgets) {
            for (name in widgets[checker]) {
                if (preferences[checker]) {
                    var defaultValue = preferences[checker][name];
                    if (typeof(defaultValue) != 'undefined') {
                        
                        var full_name = prefScope + '.' + checker + '.' + name;
                        
                        if (typeof(defaultValue) == 'boolean') {
                            var value = widgets[checker][name].checked;
                            prefset.setBooleanPref(full_name, value)
                        } else {
                            var value = widgets[checker][name].value;
                            prefset.setStringPref(full_name, value)
                        }
                        
                    }
                    
                }
            }
        }
        
    } catch(error) {
        alert(error);
    }
    return true;
}
