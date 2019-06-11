(function (jq) {
    jq('.multi-menu .item .title').click(function () {
        $(this).next(".body").toggleClass('hide');
    });
})(jQuery);

