from datetime import date, timedelta
import calendar
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .models import Event


def _make_aware(dt):
    """naive な datetime を現在のタイムゾーンで aware にする"""
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt

@login_required
def home(request):
    # ルートはカレンダーへ
    return calendar_view(request)


@login_required
def calendar_view(request):
    today = date.today()
    y = int(request.GET.get("y", today.year))
    m = int(request.GET.get("m", today.month))

    # 日曜はじまりの週グリッド（前月/翌月のはみ出しも含む）
    cal = calendar.Calendar(firstweekday=6)  # 6 = Sunday
    weeks = cal.monthdatescalendar(y, m)     # [[date x7], ...週]

    # 画面に表示される範囲でイベント取得
    start_range = weeks[0][0]
    end_range = weeks[-1][-1]
    qs = (Event.objects
          .filter(user=request.user,
                  start__date__gte=start_range,
                  start__date__lte=end_range)
          .order_by("start"))

    # date -> [Event,...]
    events_by_date = {}
    for e in qs:
        d = e.start.date()
        events_by_date.setdefault(d, []).append(e)

    # 前後月
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


# ===== JSON API =====

@login_required
def events_json(request):
    events = Event.objects.filter(user=request.user).order_by("start")
    data = [{
        "id": e.id,
        "title": e.title,
        "start": e.start.isoformat(),
        "end": e.end.isoformat() if e.end else None,
        "description": e.description,
    } for e in events]
    return JsonResponse(data, safe=False)


def _auto_end(start_dt, end_dt):
    """
    end が未指定(None/空)なら start + 3時間を返す。
    end が start より前でもガードして start + 3時間にする。
    """
    if not start_dt:
        return end_dt  # start がない場合は何もしない（上位でバリデーション）

    if end_dt is None:
        return start_dt + timedelta(hours=3)

    if end_dt <= start_dt:
        return start_dt + timedelta(hours=3)

    return end_dt


@login_required
def event_add(request):
    if request.method == "POST":
        data = json.loads(request.body)

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
            description=data.get("description", "")
        )
        return JsonResponse({"id": event.id})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def event_update(request, event_id):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            event = Event.objects.get(id=event_id, user=request.user)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)

        # start / end の更新（未指定は据え置き）
        start_dt = parse_datetime(data.get("start")) if data.get("start") else event.start
        end_dt = None
        if "end" in data:  # キーがある：空(=None)にしたいケースにも対応
            end_raw = data.get("end")
            end_dt = parse_datetime(end_raw) if end_raw else None
        else:
            end_dt = event.end  # 変更なし

        # 自動補完
        end_dt = _auto_end(start_dt, end_dt)

        event.title = data.get("title", event.title)
        event.start = start_dt
        event.end = end_dt
        event.description = data.get("description", event.description)
        event.save()
        return JsonResponse({"status": "updated"})

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def event_delete(request, event_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)
    try:
        event = Event.objects.get(id=event_id, user=request.user)
    except Event.DoesNotExist:
        return JsonResponse({"error": "Event not found"}, status=404)
    event.delete()
    return JsonResponse({"status": "deleted"})
