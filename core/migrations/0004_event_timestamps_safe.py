# core/migrations/0004_event_timestamps_safe.py
from django.db import migrations, models
from django.utils import timezone

def fill_event_timestamps(apps, schema_editor):
    Event = apps.get_model("core", "Event")
    now = timezone.now()
    # 既存行で None のものを埋める
    for e in Event.objects.filter(created_at__isnull=True):
        e.created_at = now
        if e.updated_at is None:
            e.updated_at = now
        e.save(update_fields=["created_at", "updated_at"])

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_rename_date_event_start_rename_created_by_event_user_and_more'),
    ]

    operations = [
        # まず null で追加（デフォルトは now で1回だけ使う）
        migrations.AddField(
            model_name="event",
            name="created_at",
            field=models.DateTimeField(null=True, blank=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="event",
            name="updated_at",
            field=models.DateTimeField(null=True, blank=True, default=timezone.now),
            preserve_default=False,
        ),

        # 念のため埋める（DB実装差異の保険）
        migrations.RunPython(fill_event_timestamps, migrations.RunPython.noop),

        # 仕上げ：本来の定義に変更（NOT NULL / auto_*）
        migrations.AlterField(
            model_name="event",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
