import calendar
from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from .models import Event
import json


@login_required
def home(request):
    """ホーム画面（とりあえずカレンダーを表示）"""
    return calendar_view(request)


@login_required
def calendar_view(request, year=None, month=None):
    """月ごとのカレンダー表示"""
    today = date.today()
    year = year or today.year
    month = month or today.month

    cal = calendar.Calendar(firstweekday=6)  # 日曜始まり
    month_days = cal.itermonthdates(year, month)

    events = Event.objects.filter(
        user=request.user,
        start__year=year,
        start__month=month
    )

    events_by_day = {}
    for e in events:
        day = e.start.day
        events_by_day.setdefault(day, []).append(e)

    return render(request, "core/calendar.html", {
        "year": year,
        "month": month,
        "month_days": month_days,
        "today": today,
        "events_by_day": events_by_day,
    })


@login_required
def events_json(request):
    """イベント一覧をJSONで返す"""
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


@csrf_exempt
@login_required
def event_add(request):
    """イベント追加API"""
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


@csrf_exempt
@login_required
def event_update(request, event_id):
    """イベント更新API"""
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


@csrf_exempt
@login_required
def event_delete(request, event_id):
    """イベント削除API"""
    if request.method == "POST":
        try:
            event = Event.objects.get(id=event_id, user=request.user)
            event.delete()
            return JsonResponse({"status": "deleted"})
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)
