'use strict';

class MayanImage {
    constructor (options) {
        this.element = options.element;
    }

    static async setup (options) {
        this.options = options || {};

        $().fancybox({
            afterShow: function (instance, current) {
                $('a.a-caption').on('click', function(event) {
                    instance.close(true);
                });
            },
            animationEffect: 'fade',
            animationDuration : 100,
            buttons : [
                'fullScreen',
                'close'
            ],
            idleTime: false,
            infobar: true,
            selector: 'a.fancybox',
        });
    }

    static async initialize () {
        $('img.lazy-load').each(async function(index) {
            const $this = $(this);

            $this.attr('loading', 'lazy');
            const dataURL = $this.attr('data-url');
            const url = new URL(dataURL, window.location.origin);
            $this.attr('src', url);
        });

        $('img.lazy-load-carousel').each(async function(index) {
            const $this = $(this);

            $this.attr('loading', 'lazy');
            const dataURL = $this.attr('data-url');
            const url = new URL(dataURL, window.location.origin);
            $this.attr('src', url);
        });

        $('.lazy-load').on('load', async function() {
            const $this = $(this);

            $this.siblings('.lazyload-spinner-container').remove();
            $this.removeClass('lazy-load pull-left');
            clearTimeout(MayanImage.timer);
            MayanImage.timer = setTimeout(MayanImage.timerFunction, 50);
        });

        $('.lazy-load-carousel').on('load', async function() {
            const $this = $(this);

            $this.siblings('.lazyload-spinner-container').remove();
            $this.removeClass('lazy-load-carousel pull-left');
        });
    }

    static timerFunction () {
        $.fn.matchHeight._update();
    }
}

MayanImage.timer = setTimeout(null);

$.fn.matchHeight._maintainScroll = true;
