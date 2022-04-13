/**
 * Changes active button in the Bookshelf header.
 * @param {HTMLAnchorElement} $element - User clicked tab.
 * @param {String} hideIds - Ids of the elements to hide.
 * @param {String} showId - Ids of the elements to show.
 */
function changeHeaderTab($element, hideIds, showId) {
    $(hideIds).hide(500);
    $(showId).show(500);

    let $previousActiveTab = $element.closest('.nav').find('.active');
    $previousActiveTab.removeClass('active');
    $previousActiveTab.removeClass('site-btn-outline');

    $element.addClass('active');
    $element.addClass('site-btn-outline');
}

$(function () {
    /** EventListener on click of being read button in the Bookshelf header. */
    $('#reading-link').on('click', function () {
        let hideIds = '#read-set, #must-read-set';
        let showId = '#reading-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click of read button in the Bookshelf header. */
    $('#read-link').on('click', function () {
        let hideIds = '#reading-set, #must-read-set';
        let showId = '#read-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click of must-read button in the Bookshelf header. */
    $('#must-read-link').on('click', function () {
        let hideIds = '#read-set, #reading-set';
        let showId = '#must-read-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** Event listener on click of the New Book button in the Bookshelf. */
    $('#bookshelf-new-book').on('click', function () {
        $(this).hide(500);
        $('#bookshelf-search-book-form').show(500);
        $('#search-bar').focus();
    });

    /** Event listener on click of the Undo button in the Bookshelf. */
    $('#bookshelf-hide-search').on('click', function () {
        $('#bookshelf-search-book-form').hide(500);
        $('#bookshelf-new-book').show(500);
        $('#search-bar').val("");
    });
});