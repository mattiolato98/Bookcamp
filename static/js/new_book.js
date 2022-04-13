/**
 * Populates the page with book data.
 * Called by Ajax request ajaxSearchBook.
 * @param data downloaded book data.
 */
function fillBookData(data) {
    let bookNotFoundMessage = $('#new-book-not-found-message');
    let bookAlreadyExistsMessage = $('#new-book-already-exists-message');
    let bookCoverImage = $('#new-book-cover-image');
    $('#new-book-search-error').hide();
    $('#new-book-data-box').show();

    if(data.found) {
        $('#new-book-submit-button').attr('type', 'submit');
        $('.book-not-found').hide();
        $('.book-found').show();

        if (data.has_cover_image) {
            date = new Date(); // Needed to force the image update.
            bookCoverImage.attr('src', '/static/img/book.jpeg?' + date.getTime());
        }
        else {
            bookCoverImage.hide();
        }

        $('#book-title').text(data.book_title);
        $('#book-publisher').text(data.book_publisher);
        $('#book-year').text(data.book_year);
        $('#book-language').text(data.book_language);

        if (data.book_authors.length === 1) {
            $('#book-authors-title').text('Autore');
            $('#book-authors').text(data.book_authors[0]);
        } else {
            let str_authors = "";

            for (let i = 0; i < data.book_authors.length - 1; i++)
                str_authors += data.book_authors[i] + ", ";

            $('#book-authors-title').text('Autori');
            $('#book-authors').text(str_authors + data.book_authors[data.book_authors.length - 1]);
        }
    } else {
        $('#new-book-submit-button').attr('type', '');
        $('.book-found').hide();

        if (data.already_exists) {
            bookAlreadyExistsMessage.show();
            bookNotFoundMessage.hide();
            let url = "/view/" + data.book_pk + "/public";
            $('#book-already-exists-url').attr('href', url);
        } else {
            bookAlreadyExistsMessage.hide();
            bookNotFoundMessage.show();
        }
    }
}

function fillBookDataError() {
    $('#new-book-submit-button').attr('type', '');
    $('.book-found').hide();
    $('.book-not-found').hide();
    $('#new-book-data-box').show();
    $('#new-book-search-error').show();
}

$(function () {
    // Disable submit button, preventing the form confirmation with Enter button before a book has been found.
    $('#new-book-submit-button').attr('type', '');

    /** Event listener on click del pulsante Cerca del Form di inserimento di un nuovo libro */
    $('#new-book-search-button').on('click', function () {
        let isbn = $('#isbn-code').val();
        ajaxSearchBook(isbn);
    });

    /** Event listener on change sul campo input ISBN del Form di inserimento di un nuovo libro. */
    $('#isbn-code').on('change', function () {
        let $button = $('#new-book-submit-button');
        $button.attr('type', '');
        $button.hide();
    });
});