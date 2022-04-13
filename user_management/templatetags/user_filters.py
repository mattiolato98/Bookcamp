from django.template.defaulttags import register


@register.filter
def follow(user_following, user_followed):
    """
    Checks if a user follows another one.
    :param user_following: User that follow (or not).
    :param user_followed: User followed (or not).
    :return: True if user_following follow user_followed, False otherwise.
    """
    return user_following in user_followed.profile.followers.all()

