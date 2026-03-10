function requireAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
    }
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }
    return fetch(url, { ...options, headers });
}

document.addEventListener('DOMContentLoaded', () => {
    requireAuth();
    loadUsers();
    loadAllMeetings();

    // Quick check if admin
    const userRoleStr = localStorage.getItem('user_roles');
    if (!userRoleStr || !userRoleStr.includes("ADMIN")) {
        document.body.innerHTML = '<h2 style="text-align:center; margin-top:50px; color:red;">Truy cập bị từ chối: Yêu cầu quyền ADMIN</h2><div style="text-align:center;"><a href="/">Về Trang Chủ</a></div>';
        return;
    }
});

function switchTab(tabName) {
    const tabUsers = document.getElementById('tabUsers');
    const tabMeetings = document.getElementById('tabMeetings');
    const secUsers = document.getElementById('sectionUsers');
    const secMeetings = document.getElementById('sectionMeetings');

    if (tabName === 'users') {
        tabUsers.style.background = 'var(--surface-color)';
        tabUsers.style.color = 'var(--text-color)';
        tabUsers.style.fontWeight = '600';
        tabMeetings.style.background = '#f3f4f6';
        tabMeetings.style.color = '#4b5563';
        tabMeetings.style.fontWeight = 'normal';
        secUsers.style.display = 'block';
        secMeetings.style.display = 'none';
        loadUsers();
    } else {
        tabMeetings.style.background = 'var(--surface-color)';
        tabMeetings.style.color = 'var(--text-color)';
        tabMeetings.style.fontWeight = '600';
        tabUsers.style.background = '#f3f4f6';
        tabUsers.style.color = '#4b5563';
        tabUsers.style.fontWeight = 'normal';
        secMeetings.style.display = 'block';
        secUsers.style.display = 'none';
        loadAllMeetings();
    }
}


const ROLES = [
    { id: 1, name: "ADMIN" },
    { id: 2, name: "SECRETARY" },
    { id: 3, name: "CHAIRMAN" },
    { id: 4, name: "MEMBER" },
    { id: 5, name: "VIEWER" }
];

async function loadUsers() {
    try {
        const response = await fetchWithAuth('/api/v1/users/');
        if (!response.ok) {
            document.getElementById('alertMessage').innerText = "Không thể tải dữ liệu tải khoản. Vui lòng kiểm tra quyền Admin.";
            return;
        }
        const users = await response.json();
        renderUserTable(users);
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function renderUserTable(users) {
    const tbody = document.getElementById('userTableBody');
    tbody.innerHTML = '';

    users.forEach(user => {
        const tr = document.createElement('tr');

        // Cột ID & Name
        let roleHtml = '';
        user.roles.forEach(role => {
            roleHtml += `<span class="role-badge" title="${role.description || ''}">${role.name}</span>`;
        });
        if (roleHtml === '') roleHtml = '<span style="color:gray; font-size:0.8rem;">Chưa có quyền</span>';

        // Select options for add
        let addSelectHtml = `<select class="action-select" id="addRoleSelect_${user.id}">`;
        ROLES.forEach(r => {
            addSelectHtml += `<option value="${r.id}">${r.name}</option>`;
        });
        addSelectHtml += `</select> <button class="btn btn-primary btn-sm" onclick="assignRole(${user.id})" style="padding: 4px 8px; font-size: 0.8rem;">Thêm</button>`;

        // Select options for remove (only show roles they currently have)
        let removeSelectHtml = `<select class="action-select" id="removeRoleSelect_${user.id}">`;
        if (user.roles.length > 0) {
            user.roles.forEach(r => {
                removeSelectHtml += `<option value="${r.id}">${r.name}</option>`;
            });
            removeSelectHtml += `</select> <button class="btn btn-danger btn-sm" onclick="removeRole(${user.id})" style="padding: 4px 8px; font-size: 0.8rem; background-color: var(--danger-color, #dc2626); color:white; border:none; border-radius:4px;">Gỡ bỏ</button>`;
        } else {
            removeSelectHtml = '<span style="color:gray; font-size:0.8rem;">Trống</span>';
        }

        tr.innerHTML = `
            <td>${user.id}</td>
            <td><strong>${user.username}</strong></td>
            <td>${user.full_name || '-'}</td>
            <td>${roleHtml}</td>
            <td>${addSelectHtml}</td>
            <td>${removeSelectHtml}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function assignRole(userId) {
    const roleId = document.getElementById(`addRoleSelect_${userId}`).value;
    try {
        const response = await fetchWithAuth(`/api/v1/roles/${userId}/assign/${roleId}`, {
            method: 'POST'
        });

        if (response.ok) {
            document.getElementById('alertMessage').style.color = 'green';
            document.getElementById('alertMessage').innerText = 'Cấp quyền thành công!';
            loadUsers(); // reload table
        } else {
            const data = await response.json();
            document.getElementById('alertMessage').style.color = '#b91c1c';
            document.getElementById('alertMessage').innerText = data.detail || 'Lỗi cấp quyền';
        }
    } catch (e) {
        console.error(e);
    }
}

async function removeRole(userId) {
    const roleId = document.getElementById(`removeRoleSelect_${userId}`).value;
    if (!confirm("Bạn có chắc chắn muốn thu hồi quyền này?")) return;

    try {
        const response = await fetchWithAuth(`/api/v1/roles/${userId}/remove/${roleId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            document.getElementById('alertMessage').style.color = 'green';
            document.getElementById('alertMessage').innerText = 'Thu hồi quyền thành công!';
            loadUsers(); // reload table
        } else {
            const data = await response.json();
            document.getElementById('alertMessage').style.color = '#b91c1c';
            document.getElementById('alertMessage').innerText = data.detail || 'Lỗi gỡ quyền';
        }
    } catch (e) {
        console.error(e);
    }
}

// Admin Meetings Pagination & Filters
let adminCurrentPage = 0;
const ADMIN_PAGE_SIZE = 12;

function applyAdminFilters() {
    adminCurrentPage = 0;
    loadAllMeetings();
}

function resetAdminFilters() {
    document.getElementById('adminSearchInput').value = '';
    document.getElementById('adminStatusFilter').value = 'ALL';
    document.getElementById('adminDateFrom').value = '';
    document.getElementById('adminDateTo').value = '';
    adminCurrentPage = 0;
    loadAllMeetings();
}

function loadAdminNextPage() {
    adminCurrentPage++;
    loadAllMeetings();
}

function loadAdminPrevPage() {
    if (adminCurrentPage > 0) {
        adminCurrentPage--;
        loadAllMeetings();
    }
}

async function loadAllMeetings() {
    try {
        const params = new URLSearchParams();
        params.append('skip', adminCurrentPage * ADMIN_PAGE_SIZE);
        params.append('limit', ADMIN_PAGE_SIZE);

        const search = document.getElementById('adminSearchInput')?.value;
        const status = document.getElementById('adminStatusFilter')?.value;
        let dateFrom = document.getElementById('adminDateFrom')?.value;
        let dateTo = document.getElementById('adminDateTo')?.value;

        if (search) params.append('search', search);
        if (status && status !== 'ALL') params.append('status', status);

        // Convert dates to ISO
        if (dateFrom) params.append('from_date', new Date(dateFrom + 'T00:00:00').toISOString());
        if (dateTo) params.append('to_date', new Date(dateTo + 'T23:59:59').toISOString());

        const response = await fetchWithAuth(`/api/v1/minutes/admin/all?${params.toString()}`);
        if (!response.ok) {
            console.error("Lỗi khi tải danh sách biên bản:", response.status);
            return;
        }
        const meetings = await response.json();
        renderMeetingTable(meetings);
    } catch (error) {
        console.error('Error loading meetings:', error);
    }
}

function renderMeetingTable(meetings) {
    const tbody = document.getElementById('meetingTableBody');
    tbody.innerHTML = '';

    const statusMap = {
        'NHAP': { text: 'Nháp', color: 'gray' },
        'CHO_DUYET': { text: 'Chờ duyệt', color: '#f59e0b' },
        'DA_DUYET': { text: 'Đã duyệt', color: '#3b82f6' },
        'DA_KY': { text: 'Đã ký số', color: '#10b981' },
        'LUU_TRU': { text: 'Lưu trữ', color: '#6b7280' }
    };

    meetings.forEach(meeting => {
        const tr = document.createElement('tr');

        const sInfo = statusMap[meeting.status] || { text: meeting.status, color: 'black' };
        const statusHtml = `<span style="color: ${sInfo.color}; font-weight: 500;">${sInfo.text}</span>`;

        const userNameHtml = meeting.owner_fullname
            ? `${meeting.owner_fullname} <br><small class="text-muted">(@${meeting.owner_username})</small>`
            : `<strong>@${meeting.owner_username}</strong>`;

        tr.innerHTML = `
            <td>${meeting.id}</td>
            <td>${userNameHtml}</td>
            <td><a href="/meeting/${meeting.id}" style="color: var(--primary-color); text-decoration: none;"><strong>${meeting.title}</strong></a></td>
            <td>${statusHtml}</td>
            <td>${new Date(meeting.created_at).toLocaleString('vi-VN')}</td>
            <td>
                <a href="/meeting/${meeting.id}" class="btn btn-secondary btn-sm" style="padding: 4px 8px; font-size: 0.8rem;">Xem chi tiết</a>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Add pagination controls
    let paginationRow = document.getElementById('adminPaginationRow');
    if (!paginationRow) {
        paginationRow = document.createElement('tr');
        paginationRow.id = 'adminPaginationRow';
        const td = document.createElement('td');
        td.colSpan = 6;
        td.style.textAlign = 'center';
        td.style.padding = '1rem';
        paginationRow.appendChild(td);
        tbody.parentNode.appendChild(paginationRow); // Append to table
    }

    const td = paginationRow.querySelector('td');
    td.innerHTML = `
        <div style="display: flex; justify-content: center; gap: 1rem; align-items: center;">
            <button onclick="loadAdminPrevPage()" class="btn btn-outline btn-sm" ${adminCurrentPage === 0 ? 'disabled' : ''}>← Trang trước</button>
            <span class="text-muted">Trang ${adminCurrentPage + 1}</span>
            <button onclick="loadAdminNextPage()" class="btn btn-outline btn-sm" ${meetings.length < ADMIN_PAGE_SIZE ? 'disabled' : ''}>Trang sau →</button>
        </div>
    `;

    // Move row to very end
    tbody.parentNode.appendChild(paginationRow);
}
