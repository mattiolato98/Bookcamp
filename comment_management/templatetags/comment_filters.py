from django.template.defaulttags import register
from django.utils.text import Truncator

from comment_management.models import Like, Bookmark, Comment


@register.filter
def user_likes_topic(topic, user):
    """
    Check if the user likes the Topic.
    :param topic: Topic object.
    :param user: PlatformUser object.
    :return: True if the user likes the Topic, False otherwise.
    """
    return Like.objects.filter(topic_id=topic.pk, user_owner_id=user.pk).exists()


@register.filter
def user_saved_topic(topic, user):
    """
    Check if the user has saved the Topic as a Bookmark.
    :param topic: Topic object.
    :param user: PlatformUser object.
    :return: True if the user has saved the Topic, False otherwise.
    """
    return Bookmark.objects.filter(topic_id=topic.pk, user_owner_id=user.pk).exists()


@register.filter
def filter_by_user(objects, user):
    """
    Filters objects owned by current user.
    :param objects: Generic objects.
    :param user: PlatformUser object.
    :return: Filtered object list, containing only user owned objects.
    """
    return objects.filter(user_owner=user)


@register.filter
def filter_by_user_count(objects, user):
    """
    Count user owned objects.
    :param objects: Generic objects.
    :param user: PlatformUser object.
    :return: User owned objects number.
    """
    return objects.filter(user_owner=user).count()


@register.filter
def truncate_html_chars(text, chars):
    """
    Truncates an HTML rendered text. Prevents an HTML tag from being truncated incorrectly.
    :param text: Complete text.
    :param chars: Characters to truncate the text to.
    :return: Truncated text.
    """
    truncator = Truncator(text)
    return truncator.chars(chars, html=True)
