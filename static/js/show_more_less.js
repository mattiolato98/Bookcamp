$(function () {
    /** Event listener on click del pulsante Leggi tutto di un testo troncato. */
    $('.text-show-more').on('click', function () {
        $(this).hide();
        let $box = $(this).closest('.text-box');
        $box.find('.text-show-less').show()

        let short_text = $box.find('.text-message').html();
        let complete_text = $box.find('.text-hidden-message').text();
        $box.find('.text-message').html(complete_text);
        $box.find('.text-hidden-message').text(short_text);
    });

    /** Event listenere on click del pulsante Mostra meno di un testo troncato. */
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