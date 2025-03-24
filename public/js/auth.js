async function googleLogin() {
    const response = await fetch(`${BACKEND_URL}/auth/login`);
    const data = await response.json();
    window.location.href = data.auth_url;
}

async function fetchUser() {
    const response = await fetch(`${BACKEND_URL}/auth/user`);
    const data = await response.json();
    if (data.email) {
        document.getElementById("login-link").textContent = `Hi, ${data.name.split(" ")[0]}`;
        document.getElementById("logout-button").style.display = "block";
    }
}

async function logout() {
    await fetch(`${BACKEND_URL}/auth/logout`, { method: "POST" });
    window.location.reload();
}

