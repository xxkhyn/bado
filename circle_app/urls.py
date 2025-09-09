from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # Googleログイン
    path("", views.home, name="home"),
    path("events-json/", views.events_json, name="events_json"),
    path("event/add/", views.event_add, name="event_add"),
    path("event/<int:event_id>/update/", views.event_update, name="event_update"),
    path("event/<int:event_id>/delete/", views.event_delete, name="event_delete"),
]
