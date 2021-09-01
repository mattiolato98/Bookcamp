/**
 * Riempie o svuota l'icona like a seconda del valore di data.selected. Aggiorna inoltre il numero di like.
 * Chiamata dalla richiesta Ajax ajaxSaveLike.
 * @param data Dati ritornati da Ajax.
 * @param $like_icon icona premuta dall'utente.
 */
function fillLike(data, $like_icon) {
    if(data.selected) {
        $like_icon.removeClass('like-deselected');
        $like_icon.addClass('like-selected');
    } else {
        $like_icon.removeClass('like-selected');
        $like_icon.addClass('like-deselected');
    }

    $like_icon.closest('.comment-row').find('.number-of-likes').text(data.likes_count);
}

/**
 * Riempie o svuota l'icona bookmark a seconda del valore di data.selected.
 * Chiamata dalla richiesta Ajax ajaxSaveBookmark.
 * @param data Dati ritornati da Ajax.
 * @param $bookmark_icon icona premuta dall'utente.
 */
function fillBookmark(data, $bookmark_icon) {
    if (data.selected) {
        $bookmark_icon.removeClass('bookmark-deselected');
        $bookmark_icon.addClass('bookmark-selected');
    } else {
        $bookmark_icon.removeClass('bookmark-selected');
        $bookmark_icon.addClass('bookmark-deselected');
    }
}

$(function () {
    $('[data-toggle="tooltip"]').tooltip(); // Setup dei tooltip nella pagina.

    /** Event listener on click dell'icona like. */
    $('.like-icon').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxSaveLike(pk, $(this));
    });

    /** Event listener on click dell'icona bookmark. */
    $('.bookmark-icon').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxSaveBookmark(pk, $(this));
    });
});