$(function () {
    /** Event listener on click of the button Read more of a truncated text. */
    $('.text-show-more').on('click', function () {
        $(this).hide();
        let $box = $(this).closest('.text-box');
        $box.find('.text-show-less').show()

        let short_text = $box.find('.text-message').html();
        let complete_text = $box.find('.text-hidden-message').text();
        $box.find('.text-message').html(complete_text);
        $box.find('.text-hidden-message').text(short_text);
    });

    /** Event listener on click of the button Show less of a truncated text. */
    $('.text-show-less').on('click', function () {
        $(this).hide();
        let $box = $(this).closest('.text-box');
        $box.find('.text-show-more').show();

        let complete_text = $box.find('.text-message').html();
        let short_text = $box.find('.text-hidden-message').text();
        $box.find('.text-message').html(short_text);
        $box.find('.text-hidden-message').text(complete_text);
    });
});