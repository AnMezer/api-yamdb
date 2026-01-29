from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category, Genre, Title, Review, Comment


class CategoriesGenresAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')


# Register your models here.
admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoriesAdmin(CategoriesGenresAdmin):
    pass


@admin.register(Genre)
class GenresAdmin(CategoriesGenresAdmin):
    pass


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'rating', 'description',)
    list_filter = ('year', 'rating', 'genre', 'category')
    search_fields = ('name', 'slug')
    filter_horizontal = ('genre',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'pub_date', 'score', 'title_id')
    search_fields = ('text', )
    list_filter = ('author', 'pub_date', 'score', 'title_id')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'pub_date', 'review_id')
    search_fields = ('text', )
    list_filter = ('author', 'pub_date', 'review_id')
