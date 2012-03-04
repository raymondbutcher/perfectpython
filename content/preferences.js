// Store the widget elements here.
var widgets;

// All preferences and their default values.
// A value of undefined will allow a widget to be mapped,
// without actually storing a preference.
var preferences = {
    'pep8': {
        'enabled': true,
        'warnLineLength': undefined, // Just a widget.
        'maxLineLength': 80,
    },
    'pyflakes': {
        'enabled': false
    },
    'pylint': {
        'enabled': true,
        'ignoredIds': 'C0111,C0301,C0322,C0324,I0011,R0903,R0921,W0201,W0232,W0613,W0703'
    }
}


var getPrefs = function(prefset) {
    function getOrCreate(name, defaultValue) {
        if (typeof(defaultValue) == 'boolean') {
            if (!prefset.hasPref(name)) {
                prefset.setBooleanPref(name, defaultValue);
                return defaultValue
            }
            return prefset.getBooleanPref(name);
        } else {
            if (!prefset.hasPref(name)) {
                prefset.setStringPref(name, defaultValue);
                return defaultValue
            }
            return prefset.getStringPref(name)
        }
    }
    var results = {}
    for (type in preferences) {
        results[type] = {}
        for (name in preferences[type]) {
            var defaultValue = preferences[type][name];
            if (defaultValue != undefined) {
                var id = 'perfectpython.' + type + '.' + name;
                results[type][name] = getOrCreate(id, defaultValue);
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
            widgets.pep8.maxLineLength.value = preferences.pep8.maxLineLength
        } else {
            widgets.pep8.maxLineLength.value = '';
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
    
    if (!widgets) {
        widgets = getWidgets();
    }
    
    var prefs = getPrefs(prefset);
    
    // Set up Pep8 widgets.
    widgets.pep8.enabled.checked = prefs.pep8.enabled;
    widgets.pep8.maxLineLength.value = prefs.pep8.maxLineLength;
    toggleWarnLineLength(widgets.pep8.maxLineLength);
    toggleDisabled(widgets.pep8.enabled);
    
    // Set up Pyflakes widget.
    widgets.pyflakes.enabled.checked = prefs.pyflakes.enabled;
    //toggleDisabled(widgets.pyflakes.enabled); // There are no other widgets.
    
    // Set up Pylint widgets.
    widgets.pylint.enabled.checked = prefs.pylint.enabled;
    widgets.pylint.ignoredIds.value = prefs.pylint.ignoredIds;
    //widgets.pylint.messages.view = pylintMessageView;
    toggleDisabled(widgets.pylint.enabled);
    
}
