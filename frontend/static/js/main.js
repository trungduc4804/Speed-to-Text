const API_BASE = '/api/v1';

// Utilities
function getToken() {
    return localStorage.getItem('token');
}

function checkAuth() {
    if (!getToken()) {
        window.location.href = '/login';
    }
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

// Dashboard Pagination & Filters
let currentPage = 0;
const PAGE_SIZE = 12;

function applyFilters() {
    currentPage = 0;
    loadMeetings();
}

function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = 'ALL';
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    currentPage = 0;
    loadMeetings();
}

function loadNextPage() {
    currentPage++;
    loadMeetings(true);
}

function loadPrevPage() {
    if (currentPage > 0) {
        currentPage--;
        loadMeetings();
    }
}

async function loadMeetings(append = false) {
    checkAuth();
    try {
        // Build Query String
        const params = new URLSearchParams();
        params.append('skip', currentPage * PAGE_SIZE);
        params.append('limit', PAGE_SIZE);

        const search = document.getElementById('searchInput')?.value;
        const status = document.getElementById('statusFilter')?.value;
        let dateFrom = document.getElementById('dateFrom')?.value;
        let dateTo = document.getElementById('dateTo')?.value;

        if (search) params.append('search', search);
        if (status && status !== 'ALL') params.append('status', status);

        // Convert dates to ISO strings for Python backend
        if (dateFrom) params.append('from_date', new Date(dateFrom + 'T00:00:00').toISOString());
        if (dateTo) params.append('to_date', new Date(dateTo + 'T23:59:59').toISOString());

        const response = await fetch(`${API_BASE}/minutes/?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (response.status === 401) { logout(); return; }

        const meetings = await response.json();
        const listDiv = document.getElementById('meetingList');

        if (!append) {
            listDiv.innerHTML = '';
        }

        if (meetings.length === 0 && !append) {
            listDiv.innerHTML = '<div class="text-muted" style="grid-column: 1 / -1; text-align: center; padding: 2rem;">Không tìm thấy kết quả nào.</div>';
        }

        meetings.forEach(meeting => {
            const item = document.createElement('div');
            item.className = 'meeting-card';

            const statusMap = {
                'NHAP': { text: 'Nháp', class: 'status-processed' },
                'CHO_DUYET': { text: 'Chờ duyệt', class: 'status-processed' },
                'DA_DUYET': { text: 'Đã duyệt', class: 'status-processed' },
                'DA_KY': { text: 'Đã ký số', class: 'status-signed' },
                'LUU_TRU': { text: 'Lưu trữ', class: 'status-signed' }
            };
            const sInfo = statusMap[meeting.status] || { text: 'Đang xử lý', class: 'status-processed' };
            const statusClass = sInfo.class;
            const statusText = sInfo.text;

            item.innerHTML = `
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <span class="status-badge ${statusClass}">${statusText}</span>
                        <small class="text-muted">${new Date(meeting.created_at).toLocaleDateString()}</small>
                    </div>
                    <h4 style="margin: 0 0 0.5rem 0; font-size: 1.1rem;">${meeting.title}</h4>
                </div>
                <div style="margin-top: auto; padding-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
                    <button onclick="deleteMeeting(${meeting.id})" class="btn btn-danger text-sm" style="padding: 0.5rem 1rem; font-size: 0.8rem;">Xóa</button>
                    <a href="/meeting/${meeting.id}" class="btn btn-secondary text-sm">Xem chi tiết →</a>
                </div>
            `;
            listDiv.appendChild(item);
        });

        // Handle Pagination Controls
        let paginationDiv = document.getElementById('paginationControls');
        if (!paginationDiv) {
            paginationDiv = document.createElement('div');
            paginationDiv.id = 'paginationControls';
            paginationDiv.style.gridColumn = '1 / -1';
            paginationDiv.style.display = 'flex';
            paginationDiv.style.justifyContent = 'center';
            paginationDiv.style.gap = '1rem';
            paginationDiv.style.marginTop = '2rem';
            listDiv.parentNode.insertBefore(paginationDiv, listDiv.nextSibling);
        }

        paginationDiv.innerHTML = `
            <button onclick="loadPrevPage()" class="btn btn-outline" ${currentPage === 0 ? 'disabled' : ''}>← Trang trước</button>
            <span style="display: flex; align-items: center;" class="text-muted">Trang ${currentPage + 1}</span>
            <button onclick="loadNextPage()" class="btn btn-outline" ${meetings.length < PAGE_SIZE ? 'disabled' : ''}>Trang sau →</button>
        `;

    } catch (e) {
        console.error(e);
    }
}

async function deleteMeeting(id) {
    if (!confirm("Bạn có chắc chắn muốn xóa biên bản này? Hành động này không thể hoàn tác.")) return;

    try {
        const response = await fetch(`${API_BASE}/minutes/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (response.ok) {
            alert("Đã xóa thành công!");
            loadMeetings(); // Reload list
        } else {
            alert("Xóa thất bại");
        }
    } catch (e) {
        alert("Lỗi kết nối");
    }
}

async function createMeeting(event) {
    event.preventDefault();
    const title = document.getElementById('meetingTitle').value;
    const file = document.getElementById('audioFile').files[0];

    if (!file) { alert("Vui lòng chọn file audio"); return; }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);

    const btn = event.target.querySelector('button');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang xử lý...';

    try {
        const response = await fetch(`${API_BASE}/minutes/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
            body: formData
        });

        if (response.ok) {
            alert('Tạo biên bản và chuyển đổi văn bản thành công!');
            loadMeetings();
            document.getElementById('createMeetingForm').reset();
        } else {
            const data = await response.json();
            alert(data.detail || 'Lỗi khi tạo biên bản');
        }
    } catch (e) {
        alert('Có lỗi xảy ra');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>✨ Bắt đầu xử lý</span>';
    }
}

// Detail Page
async function loadMeetingDetail(id) {
    checkAuth();
    try {
        const response = await fetch(`${API_BASE}/minutes/${id}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (response.status === 401) { logout(); return; }

        const meeting = await response.json();

        document.getElementById('title').textContent = meeting.title;
        document.getElementById('content').value = meeting.final_content || '';
        document.getElementById('audioSource').src = '/' + meeting.audio_path;

        // Render AI Data
        const summaryEl = document.getElementById('aiSummary');
        const actionItemsUl = document.getElementById('aiActionItems');

        if (meeting.summary) {
            // Replace newlines with <br> for HTML display
            summaryEl.innerHTML = meeting.summary.replace(/\ng/g, '<br>');
        } else {
            summaryEl.innerHTML = '<em>Không có tóm tắt. (Hãy nhấn Phân tích lại)</em>';
        }

        actionItemsUl.innerHTML = '';
        if (meeting.action_items) {
            try {
                const itemsList = JSON.parse(meeting.action_items);
                if (Array.isArray(itemsList) && itemsList.length > 0) {
                    itemsList.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        actionItemsUl.appendChild(li);
                    });
                } else {
                    actionItemsUl.innerHTML = '<li>Không có công việc nào được gợi ý.</li>';
                }
            } catch (e) {
                actionItemsUl.innerHTML = `<li>${meeting.action_items}</li>`;
            }
        } else {
            actionItemsUl.innerHTML = '<li>Không có công việc nào được gợi ý.</li>';
        }

        const statusEl = document.getElementById('status');
        const statusMap = {
            'NHAP': { text: 'Nháp', class: 'status-processed' },
            'CHO_DUYET': { text: 'Chờ duyệt', class: 'status-processed' },
            'DA_DUYET': { text: 'Đã duyệt', class: 'status-processed' },
            'DA_KY': { text: 'Đã ký số', class: 'status-signed' },
            'LUU_TRU': { text: 'Lưu trữ', class: 'status-signed' }
        };
        const sInfo = statusMap[meeting.status] || { text: 'Đang xử lý', class: 'status-processed' };

        statusEl.textContent = sInfo.text;
        statusEl.className = 'status-badge ' + sInfo.class;

        if (meeting.status === 'DA_KY' || meeting.status === 'LUU_TRU') {
            document.getElementById('signBtn').style.display = 'none';
            document.getElementById('saveBtn').style.display = 'none';
            document.getElementById('analyzeBtn').style.display = 'none';
            document.getElementById('content').readOnly = true;
        } else {
            // Ensure buttons exist before changing style (if they are present on page)
            const signBtn = document.getElementById('signBtn');
            const saveBtn = document.getElementById('saveBtn');
            const analyzeBtn = document.getElementById('analyzeBtn');
            if (signBtn) signBtn.style.display = 'flex';
            if (saveBtn) saveBtn.style.display = 'flex';
            if (analyzeBtn) analyzeBtn.style.display = 'flex';
            document.getElementById('content').readOnly = false;
        }

    } catch (e) {
        console.error(e);
    }
}

async function saveContent(id) {
    const content = document.getElementById('content').value;
    try {
        const response = await fetch(`${API_BASE}/minutes/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ final_content: content })
        });

        if (response.ok) {
            alert('Lưu thành công!');
        } else {
            const data = await response.json();
            alert(data.detail || 'Lỗi khi lưu');
        }
    } catch (e) {
        alert('Lỗi kết nối');
    }
}

async function exportPDF(id) {
    try {
        const response = await fetch(`${API_BASE}/pdf/export/${id}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `meeting_${id}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert('Xuất PDF thất bại');
        }
    } catch (e) {
        console.error(e);
        alert('Lỗi kết nối');
    }
}

// =====================================================================
// KÝ SỐ THỰC SỰ — Web Crypto API (RSA-PSS, SHA-256)
// Private key chỉ tồn tại trên máy người dùng, server không bao giờ thấy.
// =====================================================================

/**
 * Tạo cặp khóa RSA-PSS 2048-bit ngay trong trình duyệt.
 * - private_key.pem  → tự động download về máy người dùng
 * - public_key.pem   → tự động upload lên server và lưu vào DB
 */
async function generateKeyPair() {
    if (!confirm("Tạo cặp khóa RSA mới?\n\n⚠️ Nếu bạn đã có cặp khóa trước đó, public key cũ sẽ bị ghi đè.\nHãy bảo quản file private_key.pem cẩn thận — bạn sẽ cần nó khi ký số.")) return;

    const btn = document.getElementById('generateKeyBtn');
    if (btn) { btn.disabled = true; btn.textContent = '⏳ Đang tạo khóa...'; }

    try {
        const keyPair = await crypto.subtle.generateKey(
            { name: "RSA-PSS", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
            true, ["sign", "verify"]
        );

        // Export private key → download
        const privateKeyBuffer = await crypto.subtle.exportKey("pkcs8", keyPair.privateKey);
        downloadText("private_key.pem", bufferToPem(privateKeyBuffer, "PRIVATE KEY"));

        // Export public key → upload lên server
        const publicKeyBuffer = await crypto.subtle.exportKey("spki", keyPair.publicKey);
        const publicKeyPem = bufferToPem(publicKeyBuffer, "PUBLIC KEY");

        const formData = new FormData();
        formData.append('public_key', new Blob([publicKeyPem], { type: 'text/plain' }), 'public_key.pem');

        const response = await fetch(`${API_BASE}/signature/save-public-key`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
            body: formData
        });

        if (response.ok) {
            alert('✅ Tạo khóa thành công!\n\nFile private_key.pem đã được tải về máy bạn.\nHãy bảo quản an toàn — bạn sẽ cần nó mỗi lần ký số!');
            checkUserPublicKey();
        } else {
            const err = await response.json();
            alert('Lỗi lưu public key: ' + (err.detail || 'Unknown error'));
        }
    } catch (e) {
        console.error(e);
        alert('Lỗi tạo khóa: ' + e.message);
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = '🔑 Tạo cặp khóa mới'; }
    }
}

/**
 * Mở modal ký số. Kiểm tra public key trước.
 */
async function signPDF(id) {
    const pkRes = await fetch(`${API_BASE}/signature/public-key/me`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    const pkData = await pkRes.json();
    if (!pkData.has_public_key) {
        alert('⚠️ Bạn chưa có public key trong hệ thống.\nHãy nhấn "Tạo cặp khóa mới" trước khi ký số.');
        return;
    }
    document.getElementById('signModal').style.display = 'flex';
    document.getElementById('signMeetingId').value = id;
}

/**
 * Thực hiện ký số phía client bằng Web Crypto API, gửi signature lên server.
 */
async function executeSign() {
    const id = document.getElementById('signMeetingId').value;
    const fileInput = document.getElementById('privateKeyFile');
    if (!fileInput.files[0]) { alert('Vui lòng chọn file private_key.pem'); return; }

    const btn = document.getElementById('executeSignBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Đang ký...';

    try {
        // 1. Lấy nội dung PDF từ server
        const pdfRes = await fetch(`${API_BASE}/pdf/export/${id}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (!pdfRes.ok) { alert('Lỗi: Chưa có PDF. Hãy xuất PDF trước.'); return; }
        const pdfBuffer = await pdfRes.arrayBuffer();

        // 2. Đọc private key PEM từ file người dùng upload
        const privateKeyPem = await fileInput.files[0].text();
        const privateKey = await importPrivateKey(privateKeyPem);

        // 3. Ký dữ liệu PDF bằng RSA-PSS SHA-256
        const signatureBuffer = await crypto.subtle.sign(
            { name: "RSA-PSS", saltLength: 32 },
            privateKey,
            pdfBuffer
        );

        // 4. Encode sang base64 và gửi lên server
        const signatureBase64 = btoa(String.fromCharCode(...new Uint8Array(signatureBuffer)));

        const response = await fetch(`${API_BASE}/signature/sign/${id}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ signature: signatureBase64 })
        });

        if (response.ok) {
            closeSignModal();
            alert('✅ Ký số thành công! Biên bản đã được xác thực và khóa chỉnh sửa.');
            location.reload();
        } else {
            const err = await response.json();
            alert('❌ Ký số thất bại: ' + (err.detail || 'Unknown error'));
        }
    } catch (e) {
        console.error(e);
        alert('Lỗi khi ký: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = '✍️ Xác nhận ký số';
    }
}

function closeSignModal() {
    document.getElementById('signModal').style.display = 'none';
    document.getElementById('privateKeyFile').value = '';
}

async function checkUserPublicKey() {
    try {
        const res = await fetch(`${API_BASE}/signature/public-key/me`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        const data = await res.json();
        const indicator = document.getElementById('keyStatusIndicator');
        if (indicator) {
            indicator.textContent = data.has_public_key ? '✅ Đã có public key trong hệ thống' : '⚠️ Chưa có public key — hãy tạo cặp khóa';
            indicator.style.color = data.has_public_key ? '#16a34a' : '#d97706';
        }
    } catch (e) { /* ignore */ }
}

// ---- Helpers ----
function bufferToPem(buffer, label) {
    const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
    return `-----BEGIN ${label}-----\n${base64.match(/.{1,64}/g).join('\n')}\n-----END ${label}-----\n`;
}

function downloadText(filename, text) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

async function importPrivateKey(pem) {
    const b64 = pem.replace(/-----[^-]+-----/g, '').replace(/\s/g, '');
    const buffer = Uint8Array.from(atob(b64), c => c.charCodeAt(0)).buffer;
    return crypto.subtle.importKey("pkcs8", buffer, { name: "RSA-PSS", hash: "SHA-256" }, false, ["sign"]);
}

async function analyzeMeeting(id) {
    const btn = document.getElementById('analyzeBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Đang phân tích...';
    }

    try {
        const response = await fetch(`${API_BASE}/minutes/${id}/analyze`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (response.ok) {
            alert('Đã cập nhật tóm tắt và công việc từ AI!');
            loadMeetingDetail(id); // Reload UI
        } else {
            const data = await response.json();
            alert(data.detail || 'Phân tích AI thất bại');
        }
    } catch (e) {
        alert('Lỗi kết nối khi gọi AI');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '✨ Chạy lại AI Phân Tích';
        }
    }
}
