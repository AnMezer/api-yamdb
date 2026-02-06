from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Comment, Genre, Review, Title

admin.site.unregister(Group)


class CategoriesGenresAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')


@admin.register(Category)
class CategoriesAdmin(CategoriesGenresAdmin):
    pass


@admin.register(Genre)
class GenresAdmin(CategoriesGenresAdmin):
    pass


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'rating', 'description', 'get_genres')
    list_filter = ('genre', 'category', 'rating')
    search_fields = ('name', 'slug')
    filter_horizontal = ('genre',)

    def get_genres(self, obj):
        """Вывод жанров через запятую."""
        return ', '.join([genre.name for genre in obj.genre.all()])
    get_genres.short_description = 'Жанры'


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
