from calendar import monthrange
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime
from .models import Event
import json

@login_required
def home(request):
    # そのままカレンダーへ
    return calendar_view(request)

@login_required
def calendar_view(request):
    # ?y=2025&m=9 みたいなクエリで月移動
    try:
        year = int(request.GET.get("y", date.today().year))
        month = int(request.GET.get("m", date.today().month))
    except ValueError:
        year, month = date.today().year, date.today().month

    first_day = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    month_days = [first_day + timedelta(days=i) for i in range(days_in_month)]

    # その月にかすっている自分の予定（端が前後でも拾う）
    start_bound = datetime(year, month, 1)
    if month == 12:
        end_bound = datetime(year + 1, 1, 1)
    else:
        end_bound = datetime(year, month + 1, 1)

    events = Event.objects.filter(
        user=request.user,
        start__lt=end_bound,
        # end が null のイベントは start が範囲内かで判断したいので OR したいが簡易にこうする
    ).order_by("start")

    # 日別にまとめる（テンプレ側で参照しやすい辞書）
    events_by_day = {}
    for d in month_days:
        events_by_day[d.day] = []
    for e in events:
        d = e.start.date()
        if d.year == year and d.month == month:
            events_by_day.setdefault(d.day, []).append(e)

    # 前後月
    prev_y, prev_m = (year - 1, 12) if month == 12 else (year, month - 1)
    next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)
    if month == 1:
        prev_y, prev_m = year - 1, 12
        next_y, next_m = year, 2
    elif month == 12:
        prev_y, prev_m = year, 11
        next_y, next_m = year + 1, 1

    return render(request, "core/calendar.html", {
        "today": date.today(),
        "year": year,
        "month": month,
        "month_days": month_days,
        "events_by_day": events_by_day,
        "prev_y": prev_y, "prev_m": prev_m,
        "next_y": next_y, "next_m": next_m,
    })

# ===== JSON API（既にある人はそのままでOK） =====

@login_required
def events_json(request):
    events = Event.objects.filter(user=request.user)
    data = [
        {
            "id": e.id,
            "title": e.title,
            "start": e.start.isoformat(),
            "end": e.end.isoformat() if e.end else None,
            "description": e.description,
        }
        for e in events
    ]
    return JsonResponse(data, safe=False)

@login_required
def event_add(request):
    if request.method == "POST":
        data = json.loads(request.body)
        event = Event.objects.create(
            user=request.user,
            title=data.get("title", "無題"),
            start=parse_datetime(data["start"]),
            end=parse_datetime(data["end"]) if data.get("end") else None,
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
            event.title = data.get("title", event.title)
            event.start = parse_datetime(data["start"]) if data.get("start") else event.start
            event.end = parse_datetime(data["end"]) if data.get("end") else event.end
            event.description = data.get("description", event.description)
            event.save()
            return JsonResponse({"status": "updated"})
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def event_delete(request, event_id):
    if request.method == "POST":
        try:
            event = Event.objects.get(id=event_id, user=request.user)
            event.delete()
            return JsonResponse({"status": "deleted"})
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)
