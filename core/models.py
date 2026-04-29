# models.py
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
import uuid  # ★ 追加：トークン生成用

class User(AbstractUser):
    # 【Role Management】 ユーザーロールの定義
    # member: 一般 (カレンダー閲覧・参加のみ)
    # officer: 運営 (イベント作成・編集が可能)
    # admin: 管理者 (Django管理画面に入れる)
    class Role(models.TextChoices):
        MEMBER  = "member", "一般"
        OFFICER = "officer", "運営"
        ADMIN   = "admin",   "管理者"

    class Grade(models.TextChoices):
        B1 = "b1", "1年"
        B2 = "b2", "2年"
        B3 = "b3", "3年"
        B4 = "b4", "4年"
        B5 = "b5", "5年"
        B6 = "b6", "6年"
        M1 = "m1", "修士1年"
        M2 = "m2", "修士2年"
        D1 = "d1", "博士1年"
        D2 = "d2", "博士2年"
        D3 = "d3", "博士3年"
        OTHER = "other", "その他"

    class Faculty(models.TextChoices):
        HUMANITIES = "humanities", "人文社会科学部"
        EDUCATION = "education", "教育学部"
        SCIENCE_ENGINEERING = "science_engineering", "理工学部"
        AGRICULTURE = "agriculture", "農学部"
        VETERINARY = "veterinary", "獣医学部"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    grade = models.CharField(max_length=10, choices=Grade.choices, blank=True)
    experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    faculty = models.CharField(max_length=32, choices=Faculty.choices, blank=True)

    @property
    def is_circle_profile_complete(self):
        return bool(self.grade and self.faculty and self.experience_years is not None)


class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ★ 出席用QRコードトークン
    # 【Lazy Generation】 遅延生成パターン
    # 最初は空っぽ(null)にしておき、QRコードを表示するボタンが押された瞬間に生成する。
    # メリット：使われないイベントのために無駄なデータを生成しなくて済む。
    checkin_token = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        null=True,
        help_text="出席用QRコードに埋め込むトークン",
    )

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return self.title

    def ensure_checkin_token(self, save: bool = True) -> str:
        """
        出席用QRコードに埋め込む一意トークンを保証して返す。
        まだ無ければ uuid4 から生成して保存する。
        """
        if not self.checkin_token:
            self.checkin_token = uuid.uuid4().hex
            if save:
                self.save(update_fields=["checkin_token"])
        return self.checkin_token


class MagazineIssue(models.Model):
    title = models.CharField(max_length=200)
    issue_month = models.DateField(help_text="例: 2025-10-01")
    pdf = models.FileField(upload_to="magazines/")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issue_month", "-created_at"]

    def __str__(self):
        return self.title


# 👇 参加している人だけ1行持つ
class ChatMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    body = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user}: {self.body[:30]}"


class EventAttendance(models.Model):
    event = models.ForeignKey(
        "core.Event",
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_attendances",
    )
    # 【Reservation vs Check-in】 予約と出席の分離
    # レコード作成時 = 「予約 (参加表明)」
    # checked_in_at に日時が入る = 「出席 (現地到着)」
    # 1つのテーブルで2つの状態を管理する設計。
    checked_in_at = models.DateTimeField(null=True, blank=True, help_text="QRコードで出席記録した時間")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")
        indexes = [models.Index(fields=["event", "user"])]

    def __str__(self):
        return f"{self.user} -> {self.event}"
