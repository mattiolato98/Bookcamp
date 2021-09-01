/**
 * Funzione per cambiare pulsante attivo nell'header del profilo.
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

/**
 * Gestisce il pulsante follow/unfollow.
 * Chiamata dalla richiesta Ajax ajaxSaveFollow.
 * @param data Dati ritornati da Ajax.
 */
function changeFollow(data) {
    let start_follow_button = $('#start-follow-user');
    let stop_follow_button = $('#stop-follow-user');
    if(data.followed) {
        start_follow_button.hide();
        stop_follow_button.show();
    } else {
        stop_follow_button.hide();
        start_follow_button.show();
    }
}

$(function () {
    $('[data-toggle="tooltip"]').tooltip(); // Setup dei tooltip nella pagina.

    /** EventListener on click del pulsante Topic dell'header del profilo. */
    $('#user-profile-topics-link').on('click', function () {
        let hideIds = '#user-profile-comments-set, #user-profile-saved-topics-set, #user-profile-liked-topics-set';
        let showId = '#user-profile-topics-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click del pulsante Commenti dell'header del profilo. */
    $('#user-profile-comments-link').on('click', function () {
        let hideIds = '#user-profile-topics-set, #user-profile-saved-topics-set, #user-profile-liked-topics-set';
        let showId = '#user-profile-comments-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click del pulsante Elementi salvati dell'header del profilo. */
    $('#user-profile-saved-topics-link').on('click', function () {
        let hideIds = '#user-profile-topics-set, #user-profile-comments-set, #user-profile-liked-topics-set';
        let showId = '#user-profile-saved-topics-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click del pulsante Topic che ti piacciono dell'header del profilo. */
    $('#user-profile-liked-topics-link').on('click', function () {
        let hideIds = '#user-profile-topics-set, #user-profile-comments-set, #user-profile-saved-topics-set';
        let showId = '#user-profile-liked-topics-set';
        changeHeaderTab($(this), hideIds, showId);
    });


    /** Event listener on click del puslante Segui/Segui già. */
    $('.follow-user').on('click', function () {
       ajaxSaveFollow();
    });
});