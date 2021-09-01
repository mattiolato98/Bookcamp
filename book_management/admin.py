from django.contrib import admin

from book_management.models import Book, Author
from comment_management.models import Topic, Comment, Like, Bookmark
from user_management.models import PlatformUser, Profile, FollowRelation

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Topic)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Bookmark)
admin.site.register(PlatformUser)
admin.site.register(Profile)
admin.site.register(FollowRelation)
