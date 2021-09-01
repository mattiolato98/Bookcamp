from django.template.defaulttags import register
from django.utils.text import Truncator

from comment_management.models import Like, Bookmark, Comment


@register.filter
def user_likes_topic(topic, user):
    """
    Verifica se all'utente piace il topic.
    :param topic: Oggetto Topic.
    :param user: Oggetto PlatformUser.
    :return: True se l'utente ha messo like al topic, False altrimenti.
    """
    return Like.objects.filter(topic_id=topic.pk, user_owner_id=user.pk).exists()


@register.filter
def user_saved_topic(topic, user):
    """
    Verifica se l'utente ha salvato il topic.
    :param topic: Oggetto Topic.
    :param user: Oggetto PlatformUser.
    :return: True se l'utente ha salvato il topic, False altrimenti.
    """
    return Bookmark.objects.filter(topic_id=topic.pk, user_owner_id=user.pk).exists()


@register.filter
def filter_by_user(objects, user):
    """
    Filtra gli oggetti di proprietà dell'utente.
    :param objects: Oggetti generici.
    :param user: Oggetto PlatformUser.
    :return: Lista di oggetti filtrata, contenente solo quelli di proprietà dell'utente
    """
    return objects.filter(user_owner=user)


@register.filter
def filter_by_user_count(objects, user):
    """
    Filtra gli oggetti di proprietà dell'utente e li conta.
    :param objects: Oggetti generici.
    :param user: Oggetto PlatformUser.
    :return: Numero di oggetti nella lista filtrata, contenente solo oggetti di proprietà dell'utente.
    """
    return objects.filter(user_owner=user).count()


@register.filter
def truncate_html_chars(text, chars):
    """
    Tronca un testo renderizzato come html. Evita che un tag HTML venga troncato in maniera errata.
    :param text: Testo completo.
    :param chars: Numero di caratteri a cui troncare il testo.
    :return: Testo troncato con salvaguardia dei tag HTML.
    """
    truncator = Truncator(text)
    return truncator.chars(chars, html=True)
