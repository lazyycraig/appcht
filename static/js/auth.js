document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    async function handleLogin(e) {
        e.preventDefault();
        const submitBtn = document.getElementById('submitBtn');
        const errorMsg = document.getElementById('errorMsg');
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !password) {
            showError('Username dan password diperlukan');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Memproses...';

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'Gagal login');
                return;
            }

            // Login berhasil - redirect to dashboard
            window.location.href = '/dashboard';
        } catch (error) {
            console.error('Error:', error);
            showError('Tidak dapat terhubung ke server');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Masuk';
        }

        function showError(msg) {
            errorMsg.textContent = msg;
            errorMsg.classList.add('show');
        }
    }

    async function handleRegister(e) {
        e.preventDefault();
        const submitBtn = document.getElementById('submitBtn');
        const errorMsg = document.getElementById('errorMsg');
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const password2 = document.getElementById('password2').value;

        if (!username || !password || !password2) {
            showError('Semua field harus diisi');
            return;
        }

        if (username.length < 3) {
            showError('Username minimal 3 karakter');
            return;
        }

        if (password.length < 6) {
            showError('Password minimal 6 karakter');
            return;
        }

        if (password !== password2) {
            showError('Password tidak cocok');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Mendaftar...';

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'Gagal mendaftar');
                return;
            }

            // Register berhasil - redirect to dashboard
            window.location.href = '/dashboard';
        } catch (error) {
            console.error('Error:', error);
            showError('Tidak dapat terhubung ke server');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Daftar';
        }

        function showError(msg) {
            errorMsg.textContent = msg;
            errorMsg.classList.add('show');
        }
    }
});
