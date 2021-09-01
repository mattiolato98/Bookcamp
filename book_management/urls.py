from django.urls import path
from book_management import views

app_name = 'book_management'

urlpatterns = [
    path('new', views.NewBookView.as_view(), name='new-book'),
    path('ajax-search-book', views.ajax_search_book, name='ajax-search-book'),
]