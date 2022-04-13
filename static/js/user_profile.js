/**
 * Changes active button in the Profile header.
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

/**
 * Manages follow/unfollow button.
 * Called by Ajax request ajaxSaveFollow.
 * @param data Ajax returned data.
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
    $('[data-toggle="tooltip"]').tooltip(); // Setup Tooltip in the page

    /** EventListener on click of the button Topic in the Profile header. */
    $('#user-profile-topics-link').on('click', function () {
        let hideIds = '#user-profile-comments-set, #user-profile-saved-topics-set, #user-profile-liked-topics-set';
        let showId = '#user-profile-topics-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click of the button Comments in the Profile header. */
    $('#user-profile-comments-link').on('click', function () {
        let hideIds = '#user-profile-topics-set, #user-profile-saved-topics-set, #user-profile-liked-topics-set';
        let showId = '#user-profile-comments-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click of the button Saved elements in the Profile header. */
    $('#user-profile-saved-topics-link').on('click', function () {
        let hideIds = '#user-profile-topics-set, #user-profile-comments-set, #user-profile-liked-topics-set';
        let showId = '#user-profile-saved-topics-set';
        changeHeaderTab($(this), hideIds, showId);
    });

    /** EventListener on click of the button Topic you like in the Profile header. */
    $('#user-profile-liked-topics-link').on('click', function () {
        let hideIds = '#user-profile-topics-set, #user-profile-comments-set, #user-profile-saved-topics-set';
        let showId = '#user-profile-liked-topics-set';
        changeHeaderTab($(this), hideIds, showId);
    });


    /** Event listener on click of the button Follow/Already follow. */
    $('.follow-user').on('click', function () {
       ajaxSaveFollow();
    });
});