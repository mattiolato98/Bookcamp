/**
 * Funzione chiamata onSuccess delle richieste Ajax di inserimento, modifica ed eliminazione di libri dal bookshelf.
 * @param data Dati ritornati da Ajax.
 * @param $row Row in cui l'utente ha azionato la richiesta.
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
    $('[data-toggle="tooltip"]').tooltip(); // Setup dei tooltip nella pagina.

    /** Event listener on click dell'icona delete. */
    $('.delete-book-icon').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxDeleteBook(pk, $(this));
    });

    /** Event listener on click di Sposta in libri in lettura */
    $('.move-book-reading').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxMoveBook(pk, "READING", $(this));
    });

    /** Event listener on click di Sposta in libri letti */
    $('.move-book-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxMoveBook(pk, "READ", $(this));
    });

    /** Event listener on click di Sposta in libri da leggere */
    $('.move-book-must-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxMoveBook(pk, "MUSTREAD", $(this));
    });

    /** Event listener on click di Nuovo libro in lettura */
    $('.new-book-reading').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxNewBook(pk, "READING", $(this));
    });

    /** Event listener on click di Nuovo libro letto */
    $('.new-book-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxNewBook(pk, "READ", $(this));
    });

    /** Event listener on click di Nuovo libro da leggere */
    $('.new-book-must-read').on('click', function () {
        let pk = $(this).attr('data-post-id');
        ajaxNewBook(pk, "MUSTREAD", $(this));
    });
});