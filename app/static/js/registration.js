// app/static/js/registration.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registrationForm');
  const errorMsg = document.getElementById('errorMsg');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorMsg.textContent = '';

    const payload = {
      first_name: document.getElementById('firstName').value.trim(),
      email: document.getElementById('email').value.trim(),
      phone: document.getElementById('phone').value.trim(),
      password: document.getElementById('password').value.trim(),
    };

    try {
      const res = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      // Store email for login
      localStorage.setItem("userEmail", payload.email);

      // Redirect to main page with flash cards
      window.location.href = '/main';
    } catch (err) {
      errorMsg.textContent = err.message;
    }
  });
});
