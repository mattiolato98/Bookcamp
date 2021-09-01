from django.http import HttpResponseForbidden


def has_profile_only(func):
    """
    Decoratore per negare l'accesso a utenti che NON hanno completato il proprio profilo.
    """
    def check_and_call(request, *args, **kwargs):
        if not request.user.has_profile:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return check_and_call


def has_not_profile_only(func):
    """
    Decoratore per negare l'accesso a utenti che hanno già completato il proprio profilo.
    """
    def check_and_call(request, *args, **kwargs):
        if request.user.has_profile:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return check_and_call

