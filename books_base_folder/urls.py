"""books_base_folder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from . import views
from . import settings

urlpatterns = [
    path('grass', views.GrassView.as_view(), name='grass'),
    path('', views.HomepageView.as_view(), name='home'),
    path('search', views.SearchView.as_view(), name='search'),
    path('statistics', views.StatisticsView.as_view(), name='statistics'),
    path('user/', include('user_management.urls')),
    path('books/', include('book_management.urls')),
    path('comments/', include('comment_management.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('view/<int:pk>/public', views.PublicBookPageView.as_view(), name='view-public-book'),
    path('view/<int:pk>/private', views.PrivateBookPageView.as_view(), name='view-private-book'),
    path('notifications', views.NotificationsView.as_view(), name='notifications'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += staticfiles_urlpatterns()