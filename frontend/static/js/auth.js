async function login(event) {
  event.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const errorDiv = document.getElementById('error');

  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem('token', data.access_token);

      // Lấy thông tin User (Bao gồm Role)
      try {
        const userRes = await fetch('/api/v1/users/me', {
          headers: { 'Authorization': `Bearer ${data.access_token}` }
        });
        if (userRes.ok) {
          const userData = await userRes.json();
          const roles = userData.roles.map(r => r.name);
          localStorage.setItem('user_roles', JSON.stringify(roles));

          if (roles.includes("ADMIN")) {
            window.location.href = '/admin';
            return;
          }
        }
      } catch (e) { console.error("Lỗi lấy thông tin user", e); }

      window.location.href = '/';
    } else {
      errorDiv.textContent = data.detail || 'Login failed';
    }
  } catch (error) {
    errorDiv.textContent = 'An error occurred. Please try again.';
  }
}

async function register(event) {
  event.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const fullName = document.getElementById('fullName').value;
  const errorDiv = document.getElementById('error');

  try {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username,
        password: password,
        full_name: fullName
      })
    });

    const data = await response.json();

    if (response.ok) {
      alert('Registration successful! Please login.');
      window.location.href = '/login';
    } else {
      errorDiv.textContent = data.detail || 'Registration failed';
    }
  } catch (error) {
    errorDiv.textContent = 'An error occurred. Please try again.';
  }
}
