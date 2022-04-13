/**
 * Function to change active button in the search header.
 * @param {HTMLAnchorElement} $element - User clicked tab.
 * @param {String} hideClassName - Elements to hide classname.
 * @param {String} showClassName - Elements to show classname.
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

function initPage() {
    let search_bar = $('#search-bar');

    if (search_bar.val() === "")
        search_bar.focus();
}

$(function () {
    initPage();

    /** EventListener on clik of the button Books in the search header. */
    $('#search-header-libri').on('click', function () {
        let hideClassName = 'search-list-users';
        let showClassName = 'search-list-books';
        changeHeaderTab($(this), hideClassName, showClassName);
    });

    /** EventListener on clike of the button Users in the search header. */
    $('#search-header-utenti').on('click', function () {
        let hideClassName = 'search-list-books';
        let showClassName = 'search-list-users';
        changeHeaderTab($(this), hideClassName, showClassName);
    });
});