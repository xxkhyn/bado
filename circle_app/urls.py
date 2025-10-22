from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 管理画面 & アカウント
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),

    # メインページ
    path("", core_views.home, name="home"),
    path("calendar/", core_views.calendar_view, name="calendar"),

    # イベントAPI
    path("events-json/", core_views.events_json, name="events_json"),
    path("api/events/add/", core_views.event_add, name="event_add"),
    path("api/events/<int:event_id>/update/", core_views.event_update, name="event_update"),
    path("api/events/<int:event_id>/delete/", core_views.event_delete, name="event_delete"),
    path("api/events/<int:event_id>/vote/", core_views.event_vote, name="event_vote"),  # ← 参加トグル用

    # 月刊誌ページ
    path("magazines/", core_views.magazines_list, name="magazines_list"),
    path("magazines/upload/", core_views.magazines_upload, name="magazines_upload"),
]

# 開発環境でメディアファイルを配信
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
