from django.urls import path
from django.contrib.auth import views as auth_views
from user_management import views

app_name = 'user_management'

urlpatterns = [
    path('registration', views.UserCreateView.as_view(), name='registration'),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/view', views.UserProfileView.as_view(), name='view-profile'),
    path('profile/create', views.CreateProfileView.as_view(), name='create-profile'),
    path('profile/update', views.UpdateProfileView.as_view(), name='update-profile'),
    path('profile/delete', views.DeleteProfileView.as_view(), name='delete-profile'),
    path('delete', views.DeleteUserView.as_view(), name='delete-user'),
    path('profile/settings', views.ProfileSettingsView.as_view(), name='user-settings'),
    path('profile/settings/password', views.UpdatePasswordView.as_view(), name='user-password'),
    path('profile/<int:pk>/bookshelf', views.BookshelfView.as_view(), name='bookshelf'),
    path('profile/bookshelf/new-book', views.BookshelfNewBook.as_view(), name='bookshelf-new-book'),
    path('profile/bookshelf/<int:pk>/update', views.UpdateBookInfo.as_view(), name='bookshelf-update-book'),
    path('profile/bookshelf/reading/update', views.UpdateReadingBooks.as_view(), name='update-reading-books'),
    path('profile/bookshelf/read/update', views.UpdateReadBooks.as_view(), name='update-read-books'),
    path('profile/bookshelf/mustread/update', views.UpdateMustReadBooks.as_view(), name='update-must-read-books'),
    path('profile/following', views.FollowingUsersListView.as_view(), name='following-profiles'),
    path('profile/update/picture', views.UpdateProfilePictureView.as_view(), name='update-profile-picture'),
    path('email/verification_needed', views.EmailVerificationNeededView.as_view(), name='email-verification-needed'),
    path('email/verified', views.EmailVerifiedView.as_view(), name='email-verified'),
    path('report', views.ReportView.as_view(), name='report'),
    path('verify/<str:user_id_b64>/<str:user_token>', views.verify_user_email, name='verify-user-email'),
    path('ajax-save-follow', views.ajax_save_follow, name='ajax-save-follow'),
    path('ajax-check-username-exists', views.ajax_check_username_exists, name='ajax-check-username-exists'),
    path('ajax-delete-book', views.ajax_delete_book, name='ajax-delete-book'),
    path('ajax-move-book', views.ajax_move_book, name='ajax-move-book'),
    path('ajax-new-book', views.ajax_new_book, name='ajax-new-book'),
]