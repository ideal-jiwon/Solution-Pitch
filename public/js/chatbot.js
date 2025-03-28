document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chat-toggle-button");
    const chatbot = document.getElementById("chatbot-container");

    if (toggleBtn && chatbot) {
        toggleBtn.addEventListener("click", () => {
            chatbot.classList.toggle("show");
        });
    }
});

async function sendMessage() {
    const userInput = document.getElementById("chat-input").value.trim();
    if (!userInput) return;

    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;

    // ✅ Remind 입력 처리
    if (userInput.toLowerCase().startsWith("remind:")) {
        const note = userInput.slice(7).trim();
        try {
            const res = await fetch("/remind", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ note })
            });
            const data = await res.json();
            if (data.message) {
                chatMessages.innerHTML += `<p><strong>Bot:</strong> ✅ 알림에 저장했어요: ${note}</p>`;
            } else {
                chatMessages.innerHTML += `<p><strong>Bot:</strong> ⚠️ 저장에 실패했어요.</p>`;
            }
        } catch (err) {
            chatMessages.innerHTML += `<p><strong>Bot:</strong> ❌ 오류 발생: ${err.message}</p>`;
        }
        document.getElementById("chat-input").value = "";
        return;
    }

    // 🤖 일반 챗봇 응답 처리 (예: /chat 호출)
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });

        const data = await response.json();
        chatMessages.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
    } catch (error) {
        console.error("Error sending message:", error);
        chatMessages.innerHTML += `<p><strong>Bot:</strong> Error retrieving response.</p>`;
    }

    document.getElementById("chat-input").value = "";

}

