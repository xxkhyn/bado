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
    path("mypage/", core_views.mypage, name="mypage"),
    path("profile/edit/", core_views.profile_edit, name="profile_edit"),  # ★ プロフィール編集

    # イベントAPI
    path("events-json/", core_views.events_json, name="events_json"),
    path("api/events/add/", core_views.event_add, name="event_add"),
    path("api/events/<int:event_id>/update/", core_views.event_update, name="event_update"),
    path("api/events/<int:event_id>/delete/", core_views.event_delete, name="event_delete"),
    path("api/events/<int:event_id>/vote/", core_views.event_vote, name="event_vote"),  # ← 参加トグル用
    path("api/events/<int:event_id>/attendees/", core_views.attendees_list, name="attendees_list"),
    path("events/<int:event_id>/teams/", core_views.team_division, name="team_division"),  # ★ チーム分け

        # ★ QR 出席用
    path("events/<int:event_id>/qr/", core_views.event_qr, name="event_qr"),
    path("events/<int:event_id>/checkin/<str:token>/", core_views.event_checkin, name="event_checkin"),


    # 月刊誌ページ
    path("magazines/", core_views.magazines_list, name="magazines_list"),
    path("magazines/upload/", core_views.magazines_upload, name="magazines_upload"),

    # メンバー管理
    path("members/", core_views.member_list, name="member_list"),
    path("api/members/<int:user_id>/role/", core_views.member_update_role, name="member_update_role"),
]

# 開発環境でメディアファイルを配信
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
