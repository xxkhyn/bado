document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ja',
        editable: true,          // ドラッグ＆ドロップ有効
        selectable: true,        // クリックで追加
        events: '/events-json/',

        select: function (info) {
            let title = prompt("イベント名を入力してください:");
            if (title) {
                fetch("/events/add/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        title: title,
                        start: info.startStr,
                        end: info.endStr
                    })
                }).then(() => calendar.refetchEvents());
            }
        },

        eventChange: function (info) {  // ドラッグで日付変更
            fetch("/events/update/" + info.event.id + "/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: info.event.title,
                    start: info.event.startStr,
                    end: info.event.endStr
                })
            });
        },

        eventClick: function (info) {   // クリックで削除
            if (confirm("削除しますか？")) {
                fetch("/events/delete/" + info.event.id + "/", {
                    method: "POST"
                }).then(() => calendar.refetchEvents());
            }
        }
    });
    calendar.render();
});
