/**
 * Funzione per cambiare pulsante attivo nell'header della ricerca.
 * @param {HTMLAnchorElement} $element - tab cliccato dall'utente.
 * @param {String} hideClassName - nome della classe di cui nascondere gli elementi.
 * @param {String} showClassName - nome della classe di cui mostrare gli elementi.
 */
function changeHeaderTab($element, hideClassName, showClassName) {
    $('.' + hideClassName).hide();
    $('.'+ showClassName).show();

    let $previousActiveTab = $element.closest('.nav').find('.active');
    $previousActiveTab.removeClass('active');
    $previousActiveTab.removeClass('site-btn-outline');

    $element.addClass('active');
    $element.addClass('site-btn-outline');
}

/**
 * Inizializza la pagina con varie operazioni.
 */
function initPage() {
    let search_bar = $('#search-bar');

    if (search_bar.val() === "")
        search_bar.focus();
}

$(function () {
    initPage();

    /** EventListener on clik del pulsante "Libri" dell'header della ricerca. */
    $('#search-header-libri').on('click', function () {
        let hideClassName = 'search-list-users';
        let showClassName = 'search-list-books';
        changeHeaderTab($(this), hideClassName, showClassName);
    });

    /** EventListener on clike del pulsante "Utenti" dell'header della ricerca. */
    $('#search-header-utenti').on('click', function () {
        let hideClassName = 'search-list-books';
        let showClassName = 'search-list-users';
        changeHeaderTab($(this), hideClassName, showClassName);
    });
});