from django.contrib import admin
from .models import Event, MagazineIssue, EventAttendance


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end", "user")
    list_filter = ("user",)
    search_fields = ("title", "description")


@admin.register(MagazineIssue)
class MagazineIssueAdmin(admin.ModelAdmin):
    list_display = ("title", "issue_month", "is_public", "created_at")
    list_filter = ("is_public",)
    search_fields = ("title",)


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "created_at")
    list_filter = ("event",)
    search_fields = ("user__username", "event__title")
