/**
 * Function called by the onSuccess Ajax requests of insertion, update and deletion of books in the Bookshelf.
 * @param data Ajax returned data.
 * @param $row Row in which the user triggered the request.
 */
function bookshelfOperationSuccess(data, $row) {
    let books_count = $('#books_count')
    books_count.text(parseInt(books_count.text()) - 1);

    let operation_message = "";
    if (data.status === "deleted")
        operation_message = '<h6 class="font-6 site-red-text">' +
                            '<i class="fas fa-times"></i>&nbsp;Eliminato' +
                            '</h6>'
    else
        operation_message = '<h6 class="font-6 text-success">' +
                            '<i class="fas fa-check"></i>&nbsp;' + data.status +
                            '</h6>'

    $row.html(operation_message);
}

$(function () {
    $('[data-toggle="tooltip"]').tooltip(); // Setup Tooltip in the page

    /** Event listener on click of the Delete icon. */
    $('.delete-book-icon').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxDeleteBook(pk, $(this));
    });

        /** Event listener on click of Move to "books being read". */
    $('.move-book-reading').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxMoveBook(pk, "READING", $(this));
    });

    /** Event listener on click of Move to "read books". */
    $('.move-book-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxMoveBook(pk, "READ", $(this));
    });

    /** Event listener on click of Move to "must-read books". */
    $('.move-book-must-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxMoveBook(pk, "MUSTREAD", $(this));
    });

    /** Event listener on click of New being read book. */
    $('.new-book-reading').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxNewBook(pk, "READING", $(this));
    });

    /** Event listener on click of New read book. */
    $('.new-book-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxNewBook(pk, "READ", $(this));
    });

    /** Event listener on click of New must-read book. */
    $('.new-book-must-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxNewBook(pk, "MUSTREAD", $(this));
    });
});