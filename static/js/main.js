/**
 * PerkCart Main Client-Side JavaScript
 * - CSRF token helper
 * - AJAX Wishlist Toggle with live badge update
 * - Floating AI Assistant Widget with slide-over chat
 * - FAQ helpful/unhelpful AJAX voting
 * - Interactive UI Micro-interactions
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// ================= WISHLIST TOGGLE =================
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-wishlist-toggle').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            if (!productId) return;

            try {
                const response = await fetch(`/products/wishlist/toggle/${productId}/?format=json`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                const data = await response.json();
                if (data.status === 'success') {
                    // Update button icon
                    const icon = btn.querySelector('i');
                    if (data.is_wishlisted) {
                        btn.classList.add('active');
                        if (icon) icon.className = 'bi bi-heart-fill text-danger';
                    } else {
                        btn.classList.remove('active');
                        if (icon) icon.className = 'bi bi-heart';
                    }

                    // Update navbar wishlist badge
                    const badge = document.querySelector('#nav-wishlist-count');
                    if (badge) {
                        badge.textContent = data.total_count;
                        badge.style.display = data.total_count > 0 ? 'inline-block' : 'none';
                    }
                }
            } catch (err) {
                console.error('Wishlist error:', err);
            }
        });
    });

    // ================= FAQ VOTING =================
    document.querySelectorAll('.btn-faq-vote').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const faqId = btn.dataset.faqId;
            const voteType = btn.dataset.voteType;
            if (!faqId || !voteType) return;

            const formData = new FormData();
            formData.append('vote_type', voteType);

            try {
                const response = await fetch(`/faq/vote/${faqId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const data = await response.json();
                if (data.status === 'success' || data.status === 'already_voted') {
                    const parent = btn.closest('.faq-feedback-container');
                    if (parent) {
                        const helpfulSpan = parent.querySelector('.faq-helpful-num');
                        const unhelpfulSpan = parent.querySelector('.faq-unhelpful-num');
                        if (helpfulSpan) helpfulSpan.textContent = data.helpful_count;
                        if (unhelpfulSpan) unhelpfulSpan.textContent = data.unhelpful_count;
                        
                        const msgDiv = parent.querySelector('.faq-feedback-msg');
                        if (msgDiv) {
                            msgDiv.textContent = data.message;
                            msgDiv.className = 'faq-feedback-msg text-success small mt-1';
                        }
                    }
                }
            } catch (err) {
                console.error('FAQ Vote error:', err);
            }
        });
    });

    // ================= AI ASSISTANT CHAT WIDGET =================
    const chatInput = document.getElementById('chat-widget-input');
    const chatSendBtn = document.getElementById('chat-widget-send');
    const chatMessagesContainer = document.getElementById('chat-widget-messages');

    async function sendChatMessage(promptText) {
        const text = promptText || (chatInput ? chatInput.value.trim() : '');
        if (!text) return;

        if (chatInput) chatInput.value = '';

        // Append User Message to UI
        appendChatMessage('user', text);

        // Append Typing Loading Indicator
        const loadingId = 'loading-' + Date.now();
        appendLoadingIndicator(loadingId);
        scrollChatToBottom();

        try {
            const response = await fetch('/ai-assistant/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ query: text })
            });

            removeLoadingIndicator(loadingId);

            if (!response.ok) {
                appendChatMessage('assistant', '⚠️ Unable to connect to PerkCart AI service. Please verify your connection or try again.');
                return;
            }

            const data = await response.json();
            if (data.status === 'success') {
                appendChatMessage('assistant', data.content, data.engine, data.sources);
            } else {
                appendChatMessage('assistant', `⚠️ ${data.message || 'An error occurred.'}`);
            }
        } catch (err) {
            removeLoadingIndicator(loadingId);
            appendChatMessage('assistant', '⚠️ Network latency prevented receiving AI answer. Please retry.');
            console.error('Chat error:', err);
        }
        scrollChatToBottom();
    }

    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', () => sendChatMessage());
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    // Suggested prompt chips click handlers
    document.querySelectorAll('.suggested-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.dataset.prompt || chip.textContent.trim();
            sendChatMessage(prompt);
        });
    });

    function appendChatMessage(role, content, engine = '', sources = []) {
        if (!chatMessagesContainer) return;
        const msgWrapper = document.createElement('div');
        msgWrapper.className = `chat-bubble ${role}`;

        let formattedContent = formatMarkdown(content);
        let html = `<div>${formattedContent}</div>`;

        if (role === 'assistant' && engine) {
            html += `<div class="mt-2 text-muted small" style="font-size: 0.72rem;">
                <i class="bi bi-cpu"></i> <em>${engine}</em>
            </div>`;
        }

        if (sources && sources.length > 0) {
            html += `<div class="mt-2 pt-2 border-top border-secondary-subtle">
                <span class="small text-muted fw-bold" style="font-size: 0.72rem;">Verified Sources:</span><br>`;
            sources.forEach(src => {
                html += `<a href="${src.url}" class="chat-source-chip" target="_blank" title="${src.snippet}">
                    <i class="bi bi-box-arrow-up-right"></i> ${src.title}
                </a>`;
            });
            html += `</div>`;
        }

        msgWrapper.innerHTML = html;
        chatMessagesContainer.appendChild(msgWrapper);
    }

    function appendLoadingIndicator(id) {
        if (!chatMessagesContainer) return;
        const loader = document.createElement('div');
        loader.id = id;
        loader.className = 'chat-bubble assistant text-muted small';
        loader.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <div class="spinner-grow spinner-grow-sm text-primary" role="status"></div>
                <span>PerkCart Assistant retrieving verified corporate records...</span>
            </div>
        `;
        chatMessagesContainer.appendChild(loader);
    }

    function removeLoadingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollChatToBottom() {
        if (chatMessagesContainer) {
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        }
    }

    function formatMarkdown(text) {
        if (!text) return '';
        // Basic safe client formatting for bold, tables, lists, and links
        let res = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-primary text-decoration-underline">$1</a>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n- /g, '<br>• ')
            .replace(/\n/g, '<br>');
        return res;
    }
});
