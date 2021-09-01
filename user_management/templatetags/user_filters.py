from django.template.defaulttags import register


@register.filter
def follow(user_following, user_followed):
    """
    Verifica se utente ne segue un altro.
    :param user_following: Utente che segue/non segue.
    :param user_followed: Utente seguito/non seguito.
    :return: True se lo user_following segue lo user_followed, False altrimenti.
    """
    return user_following in user_followed.profile.followers.all()

