// Default allowed line length.
var maxLineLengthDefault = 120;

// Store the widget elements here.
var widgets;

// All preferences and their types.
// A value of undefined will allow a widget to be mapped,
// without actually linking to a preference.
var preferences = {
    'pep8': {
        'enabled': Boolean,
        'warnLineLength': undefined,
        'maxLineLength': String
    },
    'pyflakes': {
        'enabled': Boolean
    },
    'pylint': {
        'enabled': Boolean,
        'ignoredIds': String
    }
}


var getPrefs = function(prefset) {
    function getValue(name, valueType) {
        if (valueType == Boolean) {
            return prefset.getBooleanPref(name);
        } else {
            return prefset.getStringPref(name);
        }
    }
    var results = {}
    for (type in preferences) {
        results[type] = {}
        for (name in preferences[type]) {
            var valueType = preferences[type][name];
            if (valueType != undefined) {
                var full_name = 'perfectpython.' + type + '.' + name;
                try {
                    results[type][name] = getValue(full_name, valueType);
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
            widgets.pep8.maxLineLength.value = maxLineLengthDefault;
        } else {
            if (parseInt(widgets.pep8.maxLineLength.value)) {
                maxLineLengthDefault = widgets.pep8.maxLineLength.value;
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
