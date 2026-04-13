const API_BASE = '/api/v1';

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

async function loadProfile() {
    checkAuth();
    try {
        const response = await fetch(`${API_BASE}/users/me`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (response.status === 401) { logout(); return; }

        const user = await response.json();
        
        // Cập nhật giao diện readonly
        document.getElementById('usernameDisplay').textContent = user.username;
        document.getElementById('joinDateDisplay').textContent = new Date(user.created_at).toLocaleDateString();
        
        // Hiển thị chức vụ (roles)
        const rolesDiv = document.getElementById('rolesDisplay');
        rolesDiv.innerHTML = '';
        if (user.roles && user.roles.length > 0) {
            user.roles.forEach(r => {
                const badge = document.createElement('span');
                badge.className = 'status-badge status-signed'; // Re-use css class
                badge.style.marginRight = '0.5rem';
                badge.textContent = r.name;
                rolesDiv.appendChild(badge);
            });
        } else {
            rolesDiv.innerHTML = '<span class="text-muted text-sm">Chưa phân quyền</span>';
        }

        // Cập nhật giá trị vào form edit
        document.getElementById('fullNameInput').value = user.full_name || '';

    } catch (e) {
        console.error(e);
        alert('Lỗi lấy thông tin người dùng.');
    }
}

async function updateProfile(event) {
    event.preventDefault();
    
    const fullName = document.getElementById('fullNameInput').value;
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;

    const payload = {
        full_name: fullName || null
    };

    if (newPassword) {
        if (!currentPassword) {
            alert("Vui lòng nhập mật khẩu hiện tại để có thể đổi sang mật khẩu mới.");
            return;
        }
        payload.current_password = currentPassword;
        payload.new_password = newPassword;
    }

    const btn = event.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = 'Đang lưu...';
    
    const alertBox = document.getElementById('updateAlert');

    try {
        const response = await fetch(`${API_BASE}/users/me`, {
            method: 'PUT',
            headers: { 
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alertBox.style.display = 'block';
            alertBox.className = 'alert alert-success';
            alertBox.textContent = 'Cập nhật hồ sơ thành công!';
            
            // Xóa rỗng password
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            
            setTimeout(() => { alertBox.style.display = 'none'; }, 3000);
            
            // Reload lại UI cập nhật tên
            loadProfile();
        } else {
            const data = await response.json();
            alertBox.style.display = 'block';
            alertBox.className = 'alert alert-danger';
            alertBox.textContent = data.detail || 'Lỗi cập nhật.';
        }
    } catch (e) {
        alertBox.style.display = 'block';
        alertBox.className = 'alert alert-danger';
        alertBox.textContent = 'Lỗi kết nối máy chủ.';
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Lưu thay đổi';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadProfile();
});
