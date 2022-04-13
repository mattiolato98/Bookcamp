/**
 * Fills or empties Like icon, based on data.selected value and updates Likes number.
 * Called by Ajax request ajaxSaveLike.
 * @param data Ajax returned data.
 * @param $like_icon user clicked icon.
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
 * Fills or empties Bookmark icon, based on data.selected value.
 * Called by Ajax request ajaxSaveBookmark.
 * @param data Ajax returned data.
 * @param $bookmark_icon user clicked icon.
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

    /** Event listener on click of Like icon. */
    $('.like-icon').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxSaveLike(pk, $(this));
    });

    /** Event listener on click of Bookmark icon. */
    $('.bookmark-icon').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxSaveBookmark(pk, $(this));
    });
});