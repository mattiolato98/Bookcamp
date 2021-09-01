/**
 * Funzione per cambiare pulsante attivo nell'header del bookshelf.
 * @param {HTMLAnchorElement} $element - tab cliccato dall'utente.
 * @param {String} hideIds - nomi degli id di cui nascondere gli elementi.
 * @param {String} showId - nome dell'id di cui mostrare gli elementi.
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
    /** EventListener on click del pulsante In lettura dell'header del bookshelf. */
    $('#reading-link').on('click', function () {
        let hideIds = '#read-set, #must-read-set';
        let showId = '#reading-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click del pulsante In lettura dell'header del bookshelf. */
    $('#read-link').on('click', function () {
        let hideIds = '#reading-set, #must-read-set';
        let showId = '#read-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click del pulsante In lettura dell'header del bookshelf. */
    $('#must-read-link').on('click', function () {
        let hideIds = '#read-set, #reading-set';
        let showId = '#must-read-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** Event listener on click del pulsante Nuovo libro del bookshelf. */
    $('#bookshelf-new-book').on('click', function () {
        $(this).hide(500);
        $('#bookshelf-search-book-form').show(500);
        $('#search-bar').focus();
    });

    /** Event listener on click del pulsante Annulla del bookshelf. */
    $('#bookshelf-hide-search').on('click', function () {
        $('#bookshelf-search-book-form').hide(500);
        $('#bookshelf-new-book').show(500);
        $('#search-bar').val("");
    });
});