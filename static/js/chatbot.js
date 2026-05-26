/* ════════════════════════════════════════════
   CHATBOT.JS — Interface de conversation IA
   ════════════════════════════════════════════ */

const messagesEl = document.getElementById('chat-messages');
const inputEl    = document.getElementById('chat-input');
const btnSend    = document.getElementById('btn-send');

/* ─── AUTO-RESIZE TEXTAREA ─── */
inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
});

/* ─── ENVOI AVEC ENTRÉE ─── */
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

/* ─── SUGGESTIONS ─── */
function setSuggestion(text) {
  inputEl.value = text;
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
  inputEl.focus();
}

/* ─── HORODATAGE ─── */
function now() {
  return new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

/* ─── MARKDOWN BASIQUE → HTML ─── */
function mdToHtml(text) {
  return text
    // **bold**
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // *italic*
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // `code`
    .replace(/`([^`]+)`/g, '<code style="background:var(--bg);padding:1px 5px;border-radius:4px;font-size:12px">$1</code>')
    // Lists: lines starting with - or • or 📚
    .replace(/^[ \t]*[-•]\s+(.+)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul style="padding-left:18px;margin:6px 0">$1</ul>')
    // Newlines
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');
}

/* ─── AJOUTER UN BUBBLE ─── */
function addBubble(role, text, id = null) {
  const isBot   = role === 'bot';
  const avatar  = isBot ? '🤖' : '👤';
  const div     = document.createElement('div');
  div.className = `chat-bubble bubble-${role}`;
  if (id) div.id = id;

  div.innerHTML = `
    <div class="bubble-avatar">${avatar}</div>
    <div class="bubble-content">
      <div class="bubble-text">${isBot ? '<p>' + mdToHtml(text) + '</p>' : escHtml(text)}</div>
      <div class="bubble-time">${now()}</div>
    </div>
  `;

  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

/* ─── TYPING INDICATOR ─── */
function showTyping() {
  const div = document.createElement('div');
  div.className = 'chat-bubble bubble-bot typing-indicator';
  div.id = 'typing';
  div.innerHTML = `
    <div class="bubble-avatar">🤖</div>
    <div class="bubble-content">
      <div class="bubble-text">
        <div class="dots">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>
    </div>
  `;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

function escHtml(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ════════════════════════════════════════════
   ENVOYER UN MESSAGE
   ════════════════════════════════════════════ */
async function sendMessage() {
  const question = inputEl.value.trim();
  if (!question) return;

  // Afficher le message utilisateur
  addBubble('user', question);

  // Reset input
  inputEl.value = '';
  inputEl.style.height = 'auto';

  // Désactiver le bouton pendant la requête
  btnSend.disabled = true;
  showTyping();

  try {
    const res  = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await res.json();
    hideTyping();

    if (data.reponse) {
      addBubble('bot', data.reponse);
    } else {
      addBubble('bot', '❌ Une erreur est survenue. Veuillez réessayer.');
    }
  } catch (err) {
    hideTyping();
    addBubble('bot', '❌ Impossible de joindre le serveur. Vérifiez votre connexion.');
  }

  btnSend.disabled = false;
  inputEl.focus();
}

/* ─── RÉINITIALISER LA CONVERSATION ─── */
async function resetChat() {
  await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: '', reset: true })
  });

  // Vider les messages sauf le premier (bienvenue)
  const bubbles = messagesEl.querySelectorAll('.chat-bubble');
  bubbles.forEach((b, i) => { if (i > 0) b.remove(); });
}
