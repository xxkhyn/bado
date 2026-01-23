# core/views.py
from datetime import date, timedelta, datetime
import calendar
import json
import io
import io
import random  # Added for team division
from django.db.models import Count  # Added for N+1 optimization

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import qrcode

from .models import Event, MagazineIssue, EventAttendance, User
from .forms import MagazineUploadForm, ProfileForm


def _make_aware(dt):
    """naive な datetime を現在のタイムゾーンで aware にする（必要なら）"""
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


# =========================
#  画面
# =========================
@login_required
def home(request):
    """ルートはカレンダーへ"""
    return calendar_view(request)


@login_required
def calendar_view(request):
    today = date.today()
    y = int(request.GET.get("y", today.year))
    m = int(request.GET.get("m", today.month))

    # 日曜はじまりの週グリッド
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(y, m)

    # 画面に表示される範囲でイベント取得
    start_range = weeks[0][0]
    end_range = weeks[-1][-1]
    
    # datetime に変換して範囲検索（インデックス有効化のため）
    start_dt = _make_aware(datetime.combine(start_range, datetime.min.time()))
    end_dt = _make_aware(datetime.combine(end_range, datetime.max.time()))

    qs = (
        Event.objects
        .filter(start__gte=start_dt, start__lte=end_dt)
        .order_by("start")
    )

    # date -> [Event,...]
    events_by_date = {}
    for e in qs:
        d = e.start.date()
        events_by_date.setdefault(d, []).append(e)

    prev_y, prev_m = (y - 1, 12) if m == 1 else (y, m - 1)
    next_y, next_m = (y + 1, 1) if m == 12 else (y, m + 1)

    return render(request, "core/calendar.html", {
        "today": today,
        "year": y, "month": m,
        "weeks": weeks,
        "events_by_date": events_by_date,
        "prev_y": prev_y, "prev_m": prev_m,
        "next_y": next_y, "next_m": next_m,
    })


# =========================
#  イベント API
# =========================
@login_required
def events_json(request):
    # N+1問題解消: attendances の数を事前に計算しておく
    events = Event.objects.annotate(attending_count=Count("attendances")).order_by("start")
    data = [{
        "id": e.id,
        "title": e.title,
        "start": e.start.isoformat(),
        "end": e.end.isoformat() if e.end else None,
        "description": e.description,
        "attending_count": e.attending_count,  # 参加人数 (annotateで取得した値)
    } for e in events]
    return JsonResponse(data, safe=False)


def _auto_end(start_dt, end_dt):
    """end が未指定 or start 以前なら start + 3時間に補完"""
    if not start_dt:
        return end_dt
    if end_dt is None or end_dt <= start_dt:
        return start_dt + timedelta(hours=3)
    return end_dt


@login_required
@require_http_methods(["POST"])
def event_add(request):
    # 権限チェック (管理者 or 運営)
    if not (request.user.is_staff or request.user.role == User.Role.OFFICER):
        return HttpResponse(status=403)

    data = json.loads(request.body or "{}")
    start_dt = parse_datetime(data.get("start"))
    if not start_dt:
        return JsonResponse({"error": "start is required"}, status=400)

    end_raw = data.get("end")
    end_dt = parse_datetime(end_raw) if end_raw else None
    end_dt = _auto_end(start_dt, end_dt)

    event = Event.objects.create(
        user=request.user,
        title=data.get("title", "無題"),
        start=start_dt,
        end=end_dt,
        description=data.get("description", ""),
    )
    return JsonResponse({"id": event.id})


@login_required
@require_http_methods(["POST"])
def event_update(request, event_id):
    # 権限チェック (管理者 or 運営)
    if not (request.user.is_staff or request.user.role == User.Role.OFFICER):
        return HttpResponse(status=403)

    data = json.loads(request.body or "{}")
    # 編集は作成者でなくても、運営権限があれば可能とする
    event = get_object_or_404(Event, id=event_id)

    start_dt = parse_datetime(data.get("start")) if data.get("start") else event.start
    if "end" in data:
        end_raw = data.get("end")
        end_dt = parse_datetime(end_raw) if end_raw else None
    else:
        end_dt = event.end
    end_dt = _auto_end(start_dt, end_dt)

    event.title = data.get("title", event.title)
    event.start = start_dt
    event.end = end_dt
    event.description = data.get("description", event.description)
    event.save()
    return JsonResponse({"status": "updated"})


@login_required
@require_http_methods(["POST"])
def event_delete(request, event_id):
    # 権限チェック (管理者 or 運営)
    if not (request.user.is_staff or request.user.role == User.Role.OFFICER):
        return HttpResponse(status=403)

    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return JsonResponse({"status": "deleted"})


# =========================
#  参加トグル & 集計
# =========================
def _attendance_summary(event, user=None):
    """参加人数 / 自分の状態 / 表示用の参加者名（先頭10名）を返す"""
    qs = event.attendances.select_related("user").order_by("created_at")
    count = qs.count()
    names = [(u.user.first_name or u.user.username) for u in qs[:10]]
    attending = False
    if user and user.is_authenticated:
        attending = qs.filter(user=user).exists()
    return {"count": count, "attending": attending, "names": names}


@login_required
@require_http_methods(["POST"])
def event_vote(request, event_id):
    """
    参加ボタンでトグル。
    既に参加していたら取り消し、まだなら参加。
    返り値: { attending: bool, count: int, names: [...](先頭10) }
    """
    # 1. 投票対象のイベントを取得（存在しない場合は404エラー）
    event = get_object_or_404(Event, id=event_id)

    # 2. 【ロジックの安全性】 不正操作防止
    # timezone.now() は「タイムゾーンを考慮した現在時刻」を返す
    # イベント終了後は参加ステータスを変更できないように制限
    if timezone.now() > event.end:
        return JsonResponse({"error": "イベントは終了しました"}, status=403)

    # 3. 参加データの取得または作成 (get_or_create)
    # obj: 取得/作成された EventAttendance オブジェクト
    # created: 新規作成なら True, 既存なら False
    obj, created = EventAttendance.objects.get_or_create(event=event, user=request.user)
    if created:
        # 新規作成された = 「参加ボタンを押した」 = 参加状態にする
        attending = True
    else:
        # 既に存在していた = 「もう一度押してキャンセルした」 = レコードを削除する
        obj.delete()
        attending = False

    # 4. 更新後の最新集計データを取得して返す
    summary = _attendance_summary(event, request.user)
    return JsonResponse({"attending": attending, "count": summary["count"], "names": summary["names"]})


@login_required
@require_http_methods(["GET"])
def votes_summary(request, event_id):
    """
    旧フロント互換のサマリーAPI。
    yes/no/maybe は使わず、参加者のみをカウント。
    """
    event = get_object_or_404(Event, id=event_id)
    s = _attendance_summary(event, request.user)
    return JsonResponse({
        "counts": {"yes": s["count"], "maybe": 0, "no": 0, "total": s["count"]},
        "my_choice": ("yes" if s["attending"] else None),
        "yes_names": s["names"],
    })


@login_required
def attendees_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # 【N+1問題の解消】
    # .select_related('user') を付けないと、SQLが発行されまくる（参加者数N回）。
    # これを付けることで、「参加データ」と「ユーザー情報」を1回のSQLで結合(JOIN)して取得する。
    qs = event.attendances.select_related('user').order_by('created_at')
    
    names = []
    # すでにメモリ上にユーザー情報があるので、ここでのアクセスはDB通信なしで爆速
    for a in qs:
        display_name = a.user.first_name or a.user.username
        is_checked_in = (a.checked_in_at is not None)
        names.append({'name': display_name, 'checked_in': is_checked_in})
    
    # 自分が参加しているかどうか
    i_am = qs.filter(user=request.user).exists()
    return JsonResponse({'names': names, 'count': len(names), 'i_am': i_am})



# =========================
#  月刊誌
# =========================
def magazines_list(request):
    qs = MagazineIssue.objects.filter(is_public=True)
    paginator = Paginator(qs, 12)
    page = request.GET.get("page")
    issues = paginator.get_page(page)
    return render(request, "core/magazines_list.html", {"issues": issues})


@login_required
def magazines_upload(request):
    if request.method == "POST":
        form = MagazineUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("magazines_list")
    else:
        form = MagazineUploadForm()
    return render(request, "core/magazines_upload.html", {"form": form})

@login_required
def event_qr(request, event_id):
    """
    出席用QRコード画像を返すビュー。
    オーナー or スタッフのみ表示可能。
    """
    event = get_object_or_404(Event, pk=event_id)

    # 表示権限チェック（必要に応じて調整）
    if not (request.user.is_staff or request.user == event.user):
        return HttpResponse(status=403)

    token = event.ensure_checkin_token()
    checkin_url = request.build_absolute_uri(
        reverse("event_checkin", args=[event.id, token])
    )

    # QR 生成
    img = qrcode.make(checkin_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")


@login_required
def event_checkin(request, event_id, token):
    """
    QRコードから叩かれる出席登録用ビュー。
    token が Event.checkin_token と一致したら出席を記録。
    """
    # 1. イベントを取得
    event = get_object_or_404(Event, pk=event_id)

    # 2. 【トークン検証】 
    # URLに含まれるトークンが、DBの正しいトークンと一致するか確認
    # セキュリティの要：これがあるからURLを推測して出席することができない
    if not token or token != (event.checkin_token or ""):
        return HttpResponseBadRequest("無効なトークンです。")

    # 3. 参加レコードを取得（なければ作る＝飛び入り参加もOK）
    attendance, created = EventAttendance.objects.get_or_create(
        event=event,
        user=request.user,
    )

    # 4. 【出席時刻の記録】
    # まだ出席していない場合のみ、現在時刻を記録する
    if not attendance.checked_in_at:
        attendance.checked_in_at = timezone.now()
        attendance.save()
        messages.success(request, f"{event.title} の出席を記録しました。")
    else:
        # 既に記録済みならメッセージだけ変える（エラーにはしない）
        messages.info(request, f"{event.title} は既に出席済みです。")

    # 5. カレンダー画面にリダイレクトして戻す
    return redirect("calendar")


@login_required
def mypage(request):
    """マイページ: 活動履歴とスタッツを表示"""
    today = timezone.now()
    
    # 自分が参加した(している)イベントの参加情報を取得 (N+1問題対策で select_related を使用)
    all_attendances = EventAttendance.objects.filter(user=request.user).select_related('event').order_by('-event__start')
    
    # 統計 (QRチェックイン済みのものだけを「参加回数」としてカウント)
    total_count = all_attendances.filter(checked_in_at__isnull=False).count()
    
    # 予定と履歴に分割
    upcoming_attendances = all_attendances.filter(event__start__gte=today).order_by('event__start')
    past_attendances = all_attendances.filter(event__start__lt=today).order_by('-event__start')

    return render(request, "core/mypage.html", {
        "user": request.user,
        "total_count": total_count,
        "upcoming_attendances": upcoming_attendances,
        "past_attendances": past_attendances,
    })


@login_required
def team_division(request, event_id):
    """
    イベント参加者をチーム分けする。
    6人未満のチームができないように、(参加者数 // 6) チームに分割し、
    端数はラウンドロビンで配分する。
    """
    event = get_object_or_404(Event, pk=event_id)

    # 権限チェック（スタッフ or オーナー）
    if not (request.user.is_staff or request.user == event.user):
        return HttpResponse(status=403)

    # 参加者取得
    attendances = list(event.attendances.select_related('user').order_by('created_at'))
    attendees = [a.user for a in attendances]

    # シャッフル
    random.shuffle(attendees)

    total = len(attendees)
    if total == 0:
        teams = []
    else:
        # チーム数計算 (6人未満なら1チーム)
        num_teams = total // 6
        if num_teams < 1:
            num_teams = 1
        
        # チーム初期化
        teams = [[] for _ in range(num_teams)]
        
        # ラウンドロビンで割り振り
        for i, user in enumerate(attendees):
            idx = i % num_teams
            teams[idx].append(user)

    return render(request, "core/team_division.html", {
        "event": event,
        "teams": teams,
    })


# =========================
#  メンバー管理
# =========================
@login_required
def member_list(request):
    """
    メンバー一覧を表示し、役職を変更できる画面。
    管理者(is_staff) または 運営(officer) のみアクセス可能。
    """
    # 権限チェック
    if not (request.user.is_staff or request.user.role == User.Role.OFFICER):
        return HttpResponse(status=403)

    users = User.objects.all().order_by("date_joined")
    return render(request, "core/member_list.html", {"users": users, "roles": User.Role})


@login_required
@require_http_methods(["POST"])
def member_update_role(request, user_id):
    """
    ユーザーの役職を更新するAPI。
    """
    # 権限チェック
    if not (request.user.is_staff or request.user.role == User.Role.OFFICER):
        return JsonResponse({"error": "Forbidden"}, status=403)

    target_user = get_object_or_404(User, pk=user_id)
    
    # 自分自身の役職変更や、管理者の変更は慎重にすべきだが、
    # ここでは簡易的に「自分以外」かつ「相手が管理者でない」場合のみ許可するなど制限をかけるのが一般的。
    # 今回は要件がシンプルなので、そのまま通すが、自分自身の権限を剥奪すると操作できなくなるので注意。
    
    data = json.loads(request.body or "{}")
    new_role = data.get("role")
    
    if new_role not in User.Role.values:
        return JsonResponse({"error": "Invalid role"}, status=400)

    target_user.role = new_role
    target_user.save()
    
    return JsonResponse({"status": "updated", "role": target_user.get_role_display()})


@login_required
def profile_edit(request):
    """
    プロフィール編集画面。
    自分の役職（General / Officer）を変更できる。
    """
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "プロフィールを更新しました。")
            return redirect("profile_edit")
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, "core/profile_edit.html", {
        "form": form,
    })
