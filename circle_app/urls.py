from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", views.home, name="home"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("events-json/", views.events_json, name="events_json"),
    path("api/events/add/", views.event_add, name="event_add"),
    path("api/events/<int:event_id>/update/", views.event_update, name="event_update"),
    path("api/events/<int:event_id>/delete/", views.event_delete, name="event_delete"),
]
