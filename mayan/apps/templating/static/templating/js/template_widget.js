'use strict';

jQuery(document).ready(function() {
    $('[data-autocopy="true"]').change(function(event) {
        const $this = $(this);
        const $idTemplate = $this.siblings('[data-template-fields="template"]');
        const templateCursorPosition = $idTemplate.prop('selectionStart');
        let templateValue = $idTemplate.val();
        const fieldText = eval('`' + $this.data('field-template') + '`');

        templateValue = templateValue.slice(
            0, templateCursorPosition
        ) + fieldText + templateValue.slice(
            templateCursorPosition
        );
        $idTemplate.val(templateValue);
        $idTemplate.focus();
        $idTemplate.prop(
            'selectionStart', templateCursorPosition + fieldText.length
        );
        $idTemplate.prop(
            'selectionEnd', templateCursorPosition + fieldText.length
        );

        $idTemplate.trigger('change');

        $this.val('');
    });

    /* Update the code preview */

    const templatingPreviewRefresh = function () {
        const $this = $('textarea.templating-widget-code');
        const $preview = $('code.templating-widget-code');

        let content = $this.val();
        $preview.text(content);
        $preview.removeAttr('data-highlighted');
        hljs.highlightElement($preview[0]);
    }

    $('textarea.templating-widget-code').on('input change keyup', function (event) {
        templatingPreviewRefresh();
    });

    templatingPreviewRefresh();

    /* Synchronize the scrolling */

    const syncScroll = function(event) {
        const $other = $syncScrollSelector.not(this)
        const other = $other.get(0);

        $other.off('scroll', syncScroll);

        let percentage = this.scrollTop / (this.scrollHeight - this.offsetHeight);

        other.scrollTop = (other.scrollHeight - other.offsetHeight) * percentage;

        setTimeout(
            function(){
                $other.on('scroll', syncScroll);
            }, 25
        );

    }

    const $syncScrollSelector = $('textarea.templating-widget-code, code.templating-widget-code');

    $syncScrollSelector.on('scroll', syncScroll);
});
