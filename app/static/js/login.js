document.getElementById('loginForm').addEventListener('submit', async e => {
  e.preventDefault();
  const email    = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const errMsg   = document.getElementById('errorMsg');

  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  const res = await fetch('/auth/token', {
    method: 'POST',
    body: params,
  });
  if (!res.ok) {
    const err = await res.json();
    errMsg.textContent = err.detail || 'Login failed';
    return;
  }
  const { access_token } = await res.json();
  localStorage.setItem('token', access_token);
  window.location.href = '/result';
});
