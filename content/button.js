(function(){

    var imageGood = 'chrome://famfamfamsilk/skin/icons/accept.png',
        imageBad = 'chrome://famfamfamsilk/skin/icons/decline.png';

    function updateButton() {
        var view = ko.views.manager.currentView;
        if (!view || typeof(view.lintBuffer) == 'undefined' || !view.lintBuffer) {
            // No linting on this view.
            button.attributes.image.value = imageGood;
            return;
        }
        var lintResults = view.lintBuffer.lintResults,
            button = top.document.getElementById('perfectPythonToolbarButton');        
        if (lintResults == null || lintResults.getNumResults() == 0) {
            button.attributes.image.value = imageGood;
        } else {
            button.attributes.image.value = imageBad;
        }
    }

    function eventHandler() {
        // Delay execution so kolint can handle events first.
        setTimeout(updateButton, 100)
    }

    // Listen to the same events as kolint so its results can be inspected.
    // http://sourceforge.net/p/dafizilla/code/HEAD/tree/trunk/komodo/klint/src/main/content/klint/klintOverlay.js
    window.addEventListener('current_view_changed', eventHandler, false);
    window.addEventListener('current_view_check_status', eventHandler, false);
    window.addEventListener('view_opened', eventHandler, false);
    window.addEventListener('view_closed', eventHandler, false);

})();
