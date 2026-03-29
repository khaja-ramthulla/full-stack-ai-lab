let accessTokenValue = "";
let refreshTokenValue = "";

/* TAB SWITCH */
function switchTab(event, tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');

    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

/* PASSWORD VISIBILITY */
function togglePassword(id) {
    const field = document.getElementById(id);
    field.type = field.type === "password" ? "text" : "password";
}

/* SIGNUP */
async function handleSignup() {
    const email = signupEmail.value;
    const password = signupPassword.value;
    const confirm = confirmPassword.value;

    if (password !== confirm) {
        alert("Passwords do not match");
        return;
    }

    const res = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    alert(data.message || data.error);
}

/* LOGIN */
async function handleLogin() {
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: loginEmail.value,
            password: loginPassword.value
        })
    });

    const data = await res.json();

    if (!res.ok) {
        alert(data.error);
        return;
    }

    accessTokenValue = data.access_token;
    refreshTokenValue = data.refresh_token;

    authSection.style.display = 'none';
    dashboard.style.display = 'block';

    document.getElementById('welcomeText').textContent =
        `Welcome, ${data.user}!`;

    document.getElementById('accessToken').textContent = accessTokenValue;
    document.getElementById('refreshToken').textContent = refreshTokenValue;
}

/* TEST PROTECTED */
async function testProtected() {
    const res = await fetch('/api/protected', {
        headers: {
            Authorization: `Bearer ${accessTokenValue}`
        }
    });

    const data = await res.json();

    const responseArea = document.getElementById('responseArea');
    const accessMsg = document.getElementById('accessMessage');

    responseArea.style.display = 'block';
    responseArea.innerHTML = `
        <h3>Protected Route Response:</h3>
        <pre>${JSON.stringify(data, null, 2)}</pre>
    `;

    accessMsg.style.display = 'block';

    if (res.ok) {
        accessMsg.textContent = 'Access granted!';
        accessMsg.className = 'message success';
    } else {
        accessMsg.textContent = 'Access denied!';
        accessMsg.className = 'message error';
    }
}

/* REFRESH TOKEN */
async function refreshToken() {
    const res = await fetch('/api/refresh', {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${refreshTokenValue}`
        }
    });

    const data = await res.json();
    accessTokenValue = data.access_token;
    document.getElementById('accessToken').textContent = accessTokenValue;
}

/* LOGOUT */
async function logout() {
    await fetch('/api/logout', {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${accessTokenValue}`
        }
    });

    location.reload();
}
async function refreshToken() {
    const res = await fetch('/api/refresh', {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${refreshTokenValue}`
        }
    });

    const data = await res.json();
    const accessMsg = document.getElementById('accessMessage');

    if (res.ok) {
        accessTokenValue = data.access_token;
        document.getElementById('accessToken').textContent = accessTokenValue;

        accessMsg.style.display = 'block';
        accessMsg.textContent = 'Token refreshed successfully!';
        accessMsg.className = 'message success';
    } else {
        accessMsg.style.display = 'block';
        accessMsg.textContent = 'Failed to refresh token!';
        accessMsg.className = 'message error';
    }
}

