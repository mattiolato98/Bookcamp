from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin

from book_management.models import Book
from comment_management.decorators import topic_owner_only, comment_owner_only
from comment_management.forms import NewTopicCrispyForm, UpdateTopicCrispyForm, InsertCommentCrispyForm
from comment_management.models import Comment, Like, Bookmark, Topic


@login_required
@require_POST
@csrf_protect
def ajax_save_like(request):
    """
    Funzione chiamata da Ajax per salvare un like.
    Riceve una pk di un topic. Verifica se è già presente un like per l'utente della request appartenente a tale topic:
        - in caso affermativo lo elimina (l'utente sta cercando di rimuovere il like)
        - alternativamente lo aggiunge (l'utente sta cercando di aggiungere il like)
    :return: Booleano indicante se il like è stato aggiunto o rimosso, numero di like del topic dopo l'operazione.
    """
    topic_id = request.POST.get('topic_primary_key')
    selected = False

    if Like.objects.filter(topic=topic_id, user_owner_id=request.user.pk).exists():
        Like.objects.get(topic=topic_id, user_owner_id=request.user.pk).delete()
    else:
        topic_obj = Topic.objects.get(pk=topic_id)
        like = Like(user_owner_id=request.user.pk, topic=topic_obj)
        like.save()
        selected = True

    likes_count = Like.objects.filter(topic=topic_id).count()

    data = {
        'selected': selected,
        'likes_count': likes_count
    }

    return JsonResponse(data)


@login_required
@require_POST
@csrf_protect
def ajax_save_bookmark(request):
    """
     Funzione chiamata da Ajax per salvare un bookmark.
     Riceve una pk di un topic.
     Verifica se è già presente un bookmark per l'utente della request appartenente a tale topic:
         - in caso affermativo lo elimina (l'utente sta cercando di rimuovere il bookmark)
         - alternativamente lo aggiunge (l'utente sta cercando di aggiungere il bookmark)
     :return: Booleano indicante se il bookmark è stato aggiunto o rimosso.
     """
    topic_id = request.POST.get('topic_primary_key')
    selected = False

    if Bookmark.objects.filter(topic=topic_id, user_owner_id=request.user.pk).exists():
        Bookmark.objects.get(topic=topic_id, user_owner_id=request.user.pk).delete()
    else:
        topic_obj = Topic.objects.get(pk=topic_id)
        bookmark = Bookmark(user_owner_id=request.user.pk, topic=topic_obj)
        bookmark.save()
        selected = True

    data = {
        'selected': selected
    }

    return JsonResponse(data)


class NewTopicView(LoginRequiredMixin, CreateView):
    """
    View per l'inserimento di un nuovo Topic.
    Contiene il form NewTopicCrispyForm.
    """
    form_class = NewTopicCrispyForm
    template_name = 'comment_management/new_topic.html'

    def get_context_data(self, **kwargs):
        """
        Recupera i dati del libro su cui si sta cercando di pubblicare un topic.
        :return: Oggetto Book.
        """
        context = super(NewTopicView, self).get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['pk'])

        return context

    def form_valid(self, form):
        """
        Raccoglie le informazioni necessarie a completare l'inserimento.
        """
        self.object = form.save(commit=False)
        self.object.user_owner_id = self.request.user.pk
        self.object.book_id = self.kwargs['pk']
        self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        :return: redirect verso pagina 'view-book' del libro relativo al topic appena aggiunto.
        """
        return reverse_lazy('view-public-book', kwargs={'pk': self.kwargs['pk']})


@method_decorator(topic_owner_only, name='dispatch')
class UpdateTopicView(LoginRequiredMixin, UpdateView):
    """
    View per la modifica di un Topic.
    Contiene il form UpdateTopicCrispyForm.
    """
    model = Topic
    form_class = UpdateTopicCrispyForm
    template_name = "comment_management/update_topic.html"

    def get_context_data(self, **kwargs):
        """
        Recupera i dati del libro su cui è pubblicato il topic.
        :return: Oggetto Book.
        """
        context = super(UpdateTopicView, self).get_context_data(**kwargs)
        book_pk = Topic.objects.get(pk=self.kwargs['pk']).book_id
        context['book'] = Book.objects.get(pk=book_pk)

        return context

    def get_success_url(self):
        """
        :return: redirect alla pagina 'view-topic' del topic modificato.
        """
        return reverse_lazy('comment_management:view-topic', kwargs={'pk': self.kwargs['pk']})


@method_decorator(topic_owner_only, name='dispatch')
class DeleteTopicView(LoginRequiredMixin, DeleteView):
    """
    View per l'eliminazione di un Topic.
    """
    model = Topic
    template_name = 'comment_management/delete_topic.html'

    def get_success_url(self):
        """
        :return: redirect verso la pagina 'view-profile' dell'utente che fa richiesta.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


class TopicNewComment(LoginRequiredMixin, CreateView):
    """
    View per l'inserimento di un nuovo commento.
    Contiene il form InsertCommentCrispyForm.
    """
    form_class = InsertCommentCrispyForm

    def form_valid(self, form):
        """
        Raccoglie le informazioni necessarie a completare l'inserimento.
        """
        self.object = form.save(commit=False)
        self.object.user_owner_id = self.request.user.pk
        self.object.topic_id = self.kwargs['pk']
        self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        :return: redirect verso la pagina 'view-topic' del topic relativo al commento appena pubblicato.
        """
        return reverse_lazy('comment_management:view-topic', kwargs={'pk': self.kwargs['pk']})


class CommentsList(SingleObjectMixin, ListView):
    """
    View per la visualizzazione della lista di commenti di un topic.
    """
    template_name = 'comment_management/view_topic.html'
    model = Comment

    def get(self, request, *args, **kwargs):
        """
        Recupera l'oggetto topic.
        :return: Oggetto Topic.
        """
        self.object = Topic.objects.get(pk=self.kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Salva l'oggetto topic e il form nel context.
        """
        context = super(CommentsList, self).get_context_data(**kwargs)
        context['topic'] = self.object
        context['form'] = InsertCommentCrispyForm
        return context

    def get_queryset(self):
        """
        Recupera la lista di commenti del topic.
        :return: Lista di oggetti Comment.
        """
        return self.object.comments_set


class TopicPageView(View):
    """
    View della pagina per la visualizzazione di un topic, della lista dei suoi commenti.
    Fornisce un form per l'inserimento di un nuovo commento.
    """
    def get(self, request, *args, **kwargs):
        view = CommentsList.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TopicNewComment.as_view()
        return view(request, *args, **kwargs)


@method_decorator(comment_owner_only, name='dispatch')
class DeleteCommentView(LoginRequiredMixin, DeleteView):
    """
    View per l'eliminazione di un commento.
    """
    model = Comment
    template_name = 'comment_management/delete_comment.html'

    def get_context_data(self, **kwargs):
        """
        Salva nel context oggetto Topic del commento che si sta cercando di eliminare.
        :return: Oggetto Topic.
        """
        context = super(DeleteCommentView, self).get_context_data(**kwargs)
        context['topic'] = self.object.topic
        return context

    def get_success_url(self):
        """
        :return: redirect alla pagina 'view-topic' del topic relativo al commento appena eliminato.
        """
        return reverse_lazy('comment_management:view-topic', kwargs={'pk': self.object.topic_id})
