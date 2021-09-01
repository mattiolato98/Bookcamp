from django.urls import path

from comment_management import views

app_name = 'comment_management'

urlpatterns = [
    path('ajax-save-like', views.ajax_save_like, name='ajax-save-like'),
    path('ajax-save-bookmark', views.ajax_save_bookmark, name='ajax-save-bookmark'),
    path('new/topic/<int:pk>', views.NewTopicView.as_view(), name='new-topic'),
    path('update/topic/<int:pk>', views.UpdateTopicView.as_view(), name='update-topic'),
    path('delete/topic/<int:pk>', views.DeleteTopicView.as_view(), name='delete-topic'),
    path('view/topic/<int:pk>', views.TopicPageView.as_view(), name='view-topic'),
    path('delete/comment/<int:pk>', views.DeleteCommentView.as_view(), name='delete-comment'),
]
