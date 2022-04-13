from django.http import HttpResponseForbidden


def has_profile_only(func):
    """
    Decorator to deny access to users who don't have completed their profile yet.
    """
    def check_and_call(request, *args, **kwargs):
        if not request.user.has_profile:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return check_and_call


def has_not_profile_only(func):
    """
    Decorator to deny access to users who have already completed their profile.
    """
    def check_and_call(request, *args, **kwargs):
        if request.user.has_profile:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return check_and_call

