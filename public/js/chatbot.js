async function sendMessage() {
    const userInput = document.getElementById("chat-input").value;
    if (!userInput.trim()) return;

    // 사용자 입력 표시
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;

    // 백엔드 요청
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });

        const data = await response.json();

        // 챗봇 응답 표시
        chatMessages.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
    } catch (error) {
        console.error("Error sending message:", error);
        chatMessages.innerHTML += `<p><strong>Bot:</strong> Error retrieving response.</p>`;
    }

    document.getElementById("chat-input").value = "";
}
