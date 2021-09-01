$(function () {
    let clicked = false;

    $('.burger').on('click', function () {
        if (!clicked) {
            clicked = true;
            $(this).toggleClass('toggle');
            $('#navbarSupportedContent').toggle(250);
            setTimeout(function (){clicked = false;}, 250);
        }
    });

    $(document).mouseup(function (e) {
        if (window.screen.width < 992) {
            const container = $("#site-navbar");
            if (!container.is(e.target) && container.has(e.target).length === 0) {
                $('#navbarSupportedContent').hide(250);
                $('.burger').removeClass('toggle');
            }
        }
    });
});