from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Genre, Category, Game, PriceHistory, Screenshot, NewsItem, Achievement


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('recorded_at',)


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 0


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'steam_appid', 'review_score_desc', 'total_reviews', 'is_free', 'last_synced')
    list_filter = ('is_free', 'genres')
    search_fields = ('name', 'steam_appid')
    filter_horizontal = ('genres', 'categories')
    inlines = [PriceHistoryInline, ScreenshotInline, AchievementInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'published_at')
    list_filter = ('game',)
    ordering = ('-published_at',)