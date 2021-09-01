from django.http import HttpResponseNotFound

from user_management.models import ProfileBook


def profile_book_exists_only(func):
    """
    Decoratore per negare l'accesso a utenti che NON hanno completato il proprio profilo.
    """
    def check_and_call(request, *args, **kwargs):
        if not ProfileBook.objects.filter(book_id=kwargs['pk'], profile_owner_id=request.user.profile.pk).exists():
            return HttpResponseNotFound()
        return func(request, *args, **kwargs)
    return check_and_call
