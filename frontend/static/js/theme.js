// Khởi tạo ngay lập tức để tránh FOUC (Flash of Unstyled Content)
(function() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Nếu chưa từng lưu, và trình duyệt là dark thì lấy dark. Ngược lại lấy theo lưu
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
})();

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    let targetTheme = 'light';
    
    if (currentTheme !== 'dark') {
        targetTheme = 'dark';
    }
    
    document.documentElement.setAttribute('data-theme', targetTheme);
    localStorage.setItem('theme', targetTheme);
    
    // Update nút hiển thị
    updateThemeButtonIcon(targetTheme);
}

function updateThemeButtonIcon(theme) {
    const btn = document.getElementById('themeToggleBtn');
    if (btn) {
        btn.innerHTML = theme === 'dark' ? '☀️ Sáng' : '🌙 Tối';
    }
}

// Chạy lại cập nhật icon sau khi DOM đã Load (để đảm bảo button có sẵn trên giao diện HTML trước)
document.addEventListener('DOMContentLoaded', () => {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    updateThemeButtonIcon(theme);
});
