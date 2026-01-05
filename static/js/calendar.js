
// ===== CSRF =====
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
const csrftoken = getCookie('csrftoken');

// ===== Config =====
const cfg = document.getElementById('cfg');
const CAL_YEAR = parseInt(cfg.dataset.year, 10);
const CAL_MONTH = parseInt(cfg.dataset.month, 10);
const DAYS_IN_MONTH = new Date(CAL_YEAR, CAL_MONTH, 0).getDate();

// ===== Elements =====
const modalBg = document.getElementById('modalBg');
const fTitle = document.getElementById('fTitle');
const fDay = document.getElementById('fDay');
const fStartTime = document.getElementById('fStartTime');
const fEndTime = document.getElementById('fEndTime');
const fDesc = document.getElementById('fDesc');
const saveBtn = document.getElementById('saveBtn');
const delBtn = document.getElementById('deleteBtn');
const modalTitle = document.getElementById('modalTitle');

const attendBox = document.getElementById('attendBox');
const attendBtn = document.getElementById('attendBtn');
const attendCount = document.getElementById('attendCount');
const attendList = document.getElementById('attendList');

const qrBox = document.getElementById('qrBox');
const showQrBtn = document.getElementById('showQrBtn');
const qrImageWrapper = document.getElementById('qrImageWrapper');
const qrImage = document.getElementById('qrImage');

// ===== Init Day Options =====
(function initDayOptions() {
    fDay.innerHTML = '';
    for (let d = 1; d <= DAYS_IN_MONTH; d++) {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = `${d}日`;
        fDay.appendChild(opt);
    }
})();

// ===== Utils =====
const pad = (n) => String(n).padStart(2, '0');

function localPartsToISO(day, time) {
    if (!day || !time) return null;
    const [hh, mm] = time.split(':').map(Number);
    const dt = new Date(CAL_YEAR, CAL_MONTH - 1, Number(day), hh, mm, 0);
    return dt.toISOString();
}

function isoToDay(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return d.getDate();
}

function isoToTime(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// ===== Modal Logic =====
let editingId = null;
let currentCanManage = false;

function openModal(payload) {
    modalBg.style.display = 'flex';
    if (payload && payload.id) {
        editingId = payload.id;
        currentCanManage = !!payload.canManage;

        modalTitle.textContent = '予定を編集';
        fTitle.value = payload.title || '';
        fDay.value = isoToDay(payload.start) || 1;
        fStartTime.value = isoToTime(payload.start) || '09:00';
        fEndTime.value = isoToTime(payload.end) || '';
        fDesc.value = payload.description || '';

        // 権限がない場合は保存・削除ボタンを隠す
        if (payload.id && !currentCanManage) {
            saveBtn.style.display = 'none';
            delBtn.style.display = 'none';
            // 入力も無効化
            fTitle.disabled = true;
            fDay.disabled = true;
            fStartTime.disabled = true;
            fEndTime.disabled = true;
            fDesc.disabled = true;
        } else {
            saveBtn.style.display = 'inline-block';
            fTitle.disabled = false;
            fDay.disabled = false;
            fStartTime.disabled = false;
            fEndTime.disabled = false;
            fDesc.disabled = false;

            // 新規なら削除ボタンなし、既存ならあり
            if (payload.id) {
                delBtn.style.display = 'inline-block';
            } else {
                delBtn.style.display = 'none';
            }
        }

        attendBox.style.display = 'block';
        loadAttendance(editingId);

        qrBox.style.display = 'block';
        qrImageWrapper.style.display = 'none';
        qrImage.src = '';
    } else {
        // New Event
        editingId = null;
        currentCanManage = true; // Creating new event

        modalTitle.textContent = '予定を追加';
        fTitle.value = '';
        fDay.value = payload.day || 1;
        fStartTime.value = '09:00';
        fEndTime.value = '';
        fDesc.value = '';

        saveBtn.style.display = 'inline-block';
        delBtn.style.display = 'none'; // Can't delete what doesn't exist

        fTitle.disabled = false;
        fDay.disabled = false;
        fStartTime.disabled = false;
        fEndTime.disabled = false;
        fDesc.disabled = false;

        attendBox.style.display = 'none';
        attendCount.textContent = '';
        attendList.textContent = '';

        qrBox.style.display = 'none';
        qrImageWrapper.style.display = 'none';
        qrImage.src = '';
    }
}

function closeModal() {
    modalBg.style.display = 'none';
}
document.getElementById('cancelBtn').onclick = closeModal;

// Close on backdrop click
modalBg.addEventListener('click', (e) => {
    if (e.target === modalBg) closeModal();
});

// Cell Click -> New
document.querySelectorAll('.cal-cell').forEach(div => {
    div.addEventListener('click', (e) => {
        if (e.target.closest('.event-chip')) return;

        // 権限チェック
        const canAdd = (document.getElementById('cfg').dataset.canAdd === '1');
        if (!canAdd) return;

        const day = Number(div.dataset.date.split('-')[2]);
        openModal({ day: day }); // Pass day in payload
    });
});

// Event Click -> Edit
document.querySelectorAll('.event-chip').forEach(div => {
    div.addEventListener('click', (e) => {
        e.stopPropagation();
        openModal({
            id: div.dataset.id,
            title: div.dataset.title,
            start: div.dataset.start,
            end: div.dataset.end || '',
            description: div.dataset.desc || '',
            canManage: div.dataset.canManage === '1'
        });
    });
});

// Add Today Button
const addTodayBtn = document.getElementById('addTodayBtn');
if (addTodayBtn) {
    addTodayBtn.onclick = () => {
        const now = new Date();
        const sameMonth = (now.getFullYear() === CAL_YEAR) && (now.getMonth() + 1 === CAL_MONTH);
        openModal({ day: sameMonth ? now.getDate() : 1 });
    };
}


// Save
saveBtn.onclick = async () => {
    const startISO = localPartsToISO(fDay.value, fStartTime.value);
    const endISO = fEndTime.value ? localPartsToISO(fDay.value, fEndTime.value) : null;
    if (!startISO) {
        alert('開始時刻を入力してください');
        return;
    }

    if (endISO) {
        const startDate = new Date(startISO);
        const endDate = new Date(endISO);
        if (endDate <= startDate) {
            alert('終了時刻は開始時刻より後にしてください');
            return;
        }
    }
    const payload = {
        title: (fTitle.value || '').trim() || '無題',
        start: startISO,
        end: endISO,
        description: fDesc.value || ''
    };
    const url = editingId ?
        `/api/events/${editingId}/update/` :
        `/api/events/add/`;
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error();
        location.reload();
    } catch {
        alert('保存に失敗しました');
    }
};

// Delete
delBtn.onclick = async () => {
    if (!editingId) return;
    if (!confirm('本当に削除しますか？')) return;
    try {
        const res = await fetch(`/api/events/${editingId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });
        if (!res.ok) throw new Error();
        location.reload();
    } catch {
        alert('削除に失敗しました');
    }
};

// Attendance API
async function loadAttendance(eventId) {
    try {
        const res = await fetch(`/api/events/${eventId}/attendees/`);
        if (!res.ok) return;
        const data = await res.json();
        attendCount.textContent = `${data.count}名`;
        attendList.textContent = (data.names && data.names.length) ?
            data.names.join('、 ') :
            '（まだ参加者はいません）';

        const iAm = typeof data.i_am === 'boolean' ? data.i_am : false;
        updateAttendBtn(iAm);
    } catch { }
}

function updateAttendBtn(isAttending) {
    if (isAttending) {
        attendBtn.textContent = '参加中 (解除)';
        attendBtn.classList.add('active');
        attendBtn.style.background = 'var(--accent-success)';
    } else {
        attendBtn.textContent = '参加する';
        attendBtn.classList.remove('active');
        attendBtn.style.background = 'var(--brand-primary)';
    }
}

async function toggleAttendance() {
    if (!editingId) return;
    try {
        const res = await fetch(`/api/events/${editingId}/vote/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });
        if (!res.ok) {
            alert('更新に失敗しました');
            return;
        }
        const data = await res.json();
        updateAttendBtn(data.attending);
        attendCount.textContent = `${data.count}名`;
        loadAttendance(editingId); // Refresh list
    } catch {
        alert('通信エラーが発生しました');
    }
}

attendBtn.addEventListener('click', toggleAttendance);

// QR Code
showQrBtn.addEventListener('click', () => {
    if (!editingId) return;
    if (!currentCanManage) {
        alert('権限がありません');
        return;
    }
    qrImage.src = `/events/${editingId}/qr/?_=${Date.now()}`;
    qrImageWrapper.style.display = 'block';
});
