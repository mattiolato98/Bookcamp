from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
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
    Ajax called function to save a Like.
    It receives a Topic pk. It checks if a Like for the request user on the Topic already exists:
        - if so, it takes it off
        - otherwise, it adds it
    :return:
        - selected: boolean value, True if the Like has been added, False otherwise
        - likes_count: number of likes of the Topic after the operation
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
    Ajax called function to save a Bookmark.
    It receives a Topic pk. It checks if a Bookmark for the request user on the Topic already exists:
        - if so, it takes it off
        - otherwise, it adds it
     :return: boolean value, True if the Bookmark has been added, False otherwise.
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
    Topic CreateView.
    It contains NewTopicCrispyForm.
    """
    form_class = NewTopicCrispyForm
    template_name = 'comment_management/new_topic.html'

    def get_context_data(self, **kwargs):
        """
        Retrieves book data on which you are trying to post a Topic.
        :return: Book object.
        """
        context = super(NewTopicView, self).get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['pk'])

        return context

    def form_valid(self, form):
        """
        Collects additional data needed to complete the operation.
        """
        self.object = form.save(commit=False)
        self.object.user_owner_id = self.request.user.pk
        self.object.book_id = self.kwargs['pk']
        self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-book' of the book related to the just added Topic.
        """
        return reverse_lazy('view-public-book', kwargs={'pk': self.kwargs['pk']})


@method_decorator(topic_owner_only, name='dispatch')
class UpdateTopicView(LoginRequiredMixin, UpdateView):
    """
    Topic UpdateView.
    It contains UpdateTopicCrispyForm.
    """
    model = Topic
    form_class = UpdateTopicCrispyForm
    template_name = "comment_management/update_topic.html"

    def get_context_data(self, **kwargs):
        """
        Retrieves book data on which the Topic is published.
        :return: Book object.
        """
        context = super(UpdateTopicView, self).get_context_data(**kwargs)
        book_pk = Topic.objects.get(pk=self.kwargs['pk']).book_id
        context['book'] = Book.objects.get(pk=book_pk)

        return context

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-topic' of the updated Topic.
        """
        return reverse_lazy('comment_management:view-topic', kwargs={'pk': self.kwargs['pk']})


@method_decorator(topic_owner_only, name='dispatch')
class DeleteTopicView(LoginRequiredMixin, DeleteView):
    """
    Topic DeleteView.
    """
    model = Topic
    template_name = 'comment_management/delete_topic.html'

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-profile' of the requesting user.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


class TopicNewComment(LoginRequiredMixin, CreateView):
    """
    Comment CreateView.
    It contains InsertCommentCrispyForm.
    """
    form_class = InsertCommentCrispyForm

    def form_valid(self, form):
        """
        Collects additional data needed to complete the operation.
        """
        self.object = form.save(commit=False)
        self.object.user_owner_id = self.request.user.pk
        self.object.topic_id = self.kwargs['pk']
        self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-topic' of the comment related Topic.
        """
        return reverse_lazy('comment_management:view-topic', kwargs={'pk': self.kwargs['pk']})


class CommentsList(SingleObjectMixin, ListView):
    """
    Comment ListView.
    """
    template_name = 'comment_management/view_topic.html'
    model = Comment

    def get(self, request, *args, **kwargs):
        """
        Retrieves Topic object.
        :return: Topic object.
        """
        self.object = Topic.objects.get(pk=self.kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Saves Topic object and form in the context.
        """
        context = super(CommentsList, self).get_context_data(**kwargs)
        context['topic'] = self.object
        context['form'] = InsertCommentCrispyForm
        return context

    def get_queryset(self):
        """
        Retrieves Topic comment list.
        :return: Comment object list.
        """
        return self.object.comments_set


class TopicPageView(View):
    """
    Topic View, containing the Topic, the related comment list and the form to add a new comment.
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
    Comment DeleteView.
    """
    model = Comment
    template_name = 'comment_management/delete_comment.html'

    def get_context_data(self, **kwargs):
        """
        Saves Topic object of the comment you are trying to delete in the context.
        :return: Topic object.
        """
        context = super(DeleteCommentView, self).get_context_data(**kwargs)
        context['topic'] = self.object.topic
        return context

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-topic' of the Topic related to the just deleted comment.
        """
        return reverse_lazy('comment_management:view-topic', kwargs={'pk': self.object.topic_id})
