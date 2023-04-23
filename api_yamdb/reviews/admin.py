from django.contrib import admin

from .models import Category, Comment, Review, Title, User


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
