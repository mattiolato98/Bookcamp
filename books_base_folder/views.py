from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin

from books_base_folder.forms import SearchCrispyForm
from book_management.decorators import profile_book_exists_only
from book_management.models import Book
from comment_management.models import Topic
from user_management.decorators import has_profile_only
from user_management.models import Profile, ProfileBook


class SearchMixin(object):
    """
    Mixin to search data through search query.
    """
    def get_context_data(self, **kwargs):
        """
        Download books and profiles matching the search query.
        The users who do not have already completed their profile are not considered.
        :return: books and profiles the search query.
        """
        context = super(SearchMixin, self).get_context_data(**kwargs)

        search_query = self.request.GET.get('search')

        if search_query:
            books = (Book.objects.filter(title__icontains=search_query) |
                     Book.objects.filter(authors__name__icontains=search_query)).distinct()

            users = (get_user_model().objects.filter(username__icontains=search_query) |
                     get_user_model().objects.filter(email__icontains=search_query)) \
                .exclude(pk=self.request.user.pk).exclude(is_superuser=True).exclude(is_active=False) \
                .exclude(profile=None)
            profiles = (Profile.objects.filter(user__in=users) |
                        Profile.objects.filter(first_name__icontains=search_query) |
                        Profile.objects.filter(last_name__icontains=search_query)) \
                .exclude(user_id=self.request.user.pk)

            context['books'] = books
            context['profiles'] = profiles
            context['search_query'] = search_query
        else:
            context['books'] = None
            context['profiles'] = None
            context['search_query'] = None

        return context


class HomepageView(ListView):
    """
    Homepage view.
    """
    template_name = 'homepage.html'

    def get_queryset(self):
        """
        :return: 20 most recently published Topics from the user followed profiles.
        """
        if self.request.user.is_authenticated:
            followings = self.request.user.followed_profiles.all()
            users = get_user_model().objects.filter(profile__in=followings)
            topics = Topic.objects.filter(user_owner__in=users)[:20]
        else:
            topics = Topic.objects.all()[:20]

        return topics


class GrassView(TemplateView):
    """
    GRASS.
    """
    template_name = 'grass.html'


class SearchView(SearchMixin, FormView):
    """
    View to search books and profiles.
    Contains the SearchCrispyForm form.
    """
    template_name = "search_page.html"
    form_class = SearchCrispyForm

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        if context['search_query'] is not None:
            context['form'].fields['search'].widget.attrs.update({'value': context['search_query']})

        return context


class StatisticsView(TemplateView):
    """
    Global statistics page view.
    """
    template_name = 'statistics.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve popular books and profiles, by Topics number and published comments number.
        :return: popular books and profiles.
        """
        context = super(StatisticsView, self).get_context_data(**kwargs)

        popular_books = Book.get_top_5()

        popular_users_by_topics = get_user_model().get_popular_by_topics()
        popular_profiles_by_topics = [user.profile for user in popular_users_by_topics]

        popular_users_by_comments = get_user_model().get_popular_by_comments()
        popular_profiles_by_comments = [user.profile for user in popular_users_by_comments]

        context['popular_books'] = popular_books
        context['popular_profiles_by_topics'] = popular_profiles_by_topics
        context['popular_profiles_by_comments'] = popular_profiles_by_comments
        return context


class PublicBookPageView(SingleObjectMixin, ListView):
    """
    Public book page view, containing book information and book related Topics.
    """
    template_name = 'view_public_book.html'
    model = Topic

    def get(self, request, *args, **kwargs):
        """
        Retrieve Book object.
        """
        self.object = Book.objects.get(pk=self.kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Saves Book object retrieved in the context.
        :return: Book object.
        """
        context = super(PublicBookPageView, self).get_context_data(**kwargs)
        context['book'] = self.object
        return context

    def get_queryset(self):
        """
        Retrieve Topics list related to the book.
        :return: Topics list of the book retrieved in the get function.
        """
        return self.object.topics_set


@method_decorator([login_required, has_profile_only, profile_book_exists_only], name='dispatch')
class PrivateBookPageView(TemplateView):
    template_name = "view_private_book.html"

    def get_context_data(self, **kwargs):
        """
        Retrieve Book object.
        """
        context = super(PrivateBookPageView, self).get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['pk'])
        context['profile_book'] = \
            ProfileBook.objects.get(book_id=self.kwargs['pk'], profile_owner_id=self.request.user.profile.pk)
        return context


@method_decorator([login_required, has_profile_only], name='dispatch')
class NotificationsView(TemplateView):
    template_name = 'notifications.html'
