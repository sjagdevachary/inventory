/**
 * Chatbot Widget JavaScript
 * Handles chatbot toggle, message sending, and response rendering
 */

// ── Toggle Chatbot Window ──────────────────────────
function toggleChatbot() {
    const window = document.getElementById('chatbotWindow');
    window.classList.toggle('show');

    // Focus input when opening
    if (window.classList.contains('show')) {
        document.getElementById('chatInput').focus();
    }
}

// ── Send Chat Message ──────────────────────────────
async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    // Show user message
    addMessage(message, 'user');
    input.value = '';

    try {
        const res = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await res.json();

        // Parse markdown-like bold syntax
        const formattedResponse = data.response
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        addMessage(formattedResponse, 'bot');
    } catch (err) {
        addMessage('❌ Sorry, I couldn\'t process your request. Please try again.', 'bot');
    }
}

// ── Add Message to Chat ────────────────────────────
function addMessage(content, sender) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `chat-message ${sender}`;
    div.innerHTML = content;
    container.appendChild(div);

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// ── Mobile Sidebar Toggle ──────────────────────────
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}
