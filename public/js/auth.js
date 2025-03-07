async function googleLogin() {
    try {
        const response = await fetch("http://127.0.0.1:5000/auth/login");
        const data = await response.json();
        window.location.href = data.auth_url;
    } catch (error) {
        console.error("Login error:", error);
    }
}

async function fetchUser() {
    try {
        const response = await fetch("http://127.0.0.1:5000/auth/user");
        const data = await response.json();

        if (data.email) {
            document.getElementById("login-container").style.display = "none";
            document.getElementById("logout-button").style.display = "block";
            document.getElementById("login-link").textContent = `Hi, ${data.name.split(" ")[0]}`;
            document.getElementById("login-link").href = "#";  // 로그인된 상태에서는 이동 방지
        }
    } catch (error) {
        console.error("Error fetching user:", error);
    }
}

async function logout() {
    try {
        await fetch("http://127.0.0.1:5000/auth/logout", { method: "POST" });
        window.location.reload();
    } catch (error) {
        console.error("Logout error:", error);
    }
}

fetchUser();

