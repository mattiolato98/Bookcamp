/**
 * Hides box information.
 * @param {HTMLDivElement} $element User clicked button.
 */
function hideBoxData($element) {
    $('#view-box-information').slideUp();
    $('.box-data-hide').show();
    $('.box-data-show').hide();

    $element.closest('.container-fluid').removeClass('p-4');
    $element.closest('.container-fluid').addClass('p-2');
    $element.addClass('mt-2');
    $element.toggleClass('collapse-box-data expand-box-data');
}

/**
 * Shows box information.
 * @param {HTMLDivElement} $element User clicked button.
 */
function showBoxData($element) {
    $('#view-box-information').slideDown();
    $('.box-data-hide').hide();
    $('.box-data-show').show();

    $element.closest('.container-fluid').removeClass('p-2');
    $element.closest('.container-fluid').addClass('p-4');
    $element.removeClass('mt-2');
    $element.toggleClass('expand-box-data collapse-box-data');

    $('#new-comment-field').focus();
}

$(function () {
    /** Event listener on click of the button to show/hide book information. */
    $('.collapse-box-data, .expand-box-data').on('click', function () {
        if ($(this).hasClass('collapse-box-data'))
            hideBoxData($(this));
        else if ($(this).hasClass('expand-box-data'))
            showBoxData($(this));
    });
});