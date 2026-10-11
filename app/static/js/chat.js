/**
 * Chat Module: Grounded Study Companion Dialogue
 */

window.ChatModule = {
  isProcessing: false,
  recognition: null,

  init() {
    this.messagesContainer = document.getElementById('chatMessages');
    this.chatInput = document.getElementById('chatInput');
    this.sendBtn = document.getElementById('sendChatBtn');
    this.micBtn = document.getElementById('micBtn');

    if (!this.messagesContainer) return;

    this.sendBtn.addEventListener('click', () => this.handleSend());
    this.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.handleSend();
      }
    });

    // Voice recognition setup
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRec();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = 'en-US';

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.chatInput.value = transcript;
        this.micBtn.classList.remove('voice-active');
        this.handleSend();
      };

      this.recognition.onerror = () => {
        this.micBtn.classList.remove('voice-active');
      };

      this.recognition.onend = () => {
        this.micBtn.classList.remove('voice-active');
      };

      this.micBtn.addEventListener('click', () => {
        try {
          this.recognition.start();
          this.micBtn.classList.add('voice-active');
        } catch (e) {
          this.recognition.stop();
          this.micBtn.classList.remove('voice-active');
        }
      });
    } else {
      this.micBtn.style.display = 'none';
    }

    // Bind suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const q = chip.getAttribute('data-query');
        this.chatInput.value = q;
        this.handleSend();
      });
    });
  },

  async handleSend() {
    const text = this.chatInput.value.trim();
    if (!text || this.isProcessing) return;

    this.isProcessing = true;
    this.chatInput.value = '';

    // Append User Message
    this.appendMessage('user', text);

    // Append Loading indicator
    const loadingId = 'loading-' + Date.now();
    this.appendLoadingBubble(loadingId);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          bilingual_mode: AppState.bilingualMode,
          persona: AppState.activePersona || 'professor',
          api_key_override: AppState.apiKey || null
        })
      });

      this.removeLoadingBubble(loadingId);

      if (!res.ok) throw new Error('Failed to fetch tutor response');
      const data = await res.json();

      this.appendBotMessage(data);

      if (AppState.voiceMode && data.answer) {
        speakText(data.answer);
      }
    } catch (err) {
      this.removeLoadingBubble(loadingId);
      this.appendMessage('bot', `⚠️ Error communicating with study companion: ${err.message}`);
    } finally {
      this.isProcessing = false;
      this.chatInput.focus();
    }
  },

  appendMessage(role, content) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${role === 'user' ? 'user-msg' : 'bot-msg'}`;
    
    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.innerHTML = role === 'user' 
      ? '<span>You (Student)</span>' 
      : '<span class="bot-avatar-badge">🧠 SynapseLearn AI</span>';
    
    const body = document.createElement('div');
    body.innerHTML = this.formatMarkdown(content);

    bubble.appendChild(meta);
    bubble.appendChild(body);
    this.messagesContainer.appendChild(bubble);
    this.scrollToBottom();
  },

  appendBotMessage(data) {
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble bot-msg';

    const meta = document.createElement('div');
    meta.className = 'message-meta';
    
    let statusBadge = '';
    if (!data.is_grounded) {
      statusBadge = '<span class="refusal-badge">⛔ Refusal: Out of Course Material</span>';
    } else {
      statusBadge = `<span style="color: #2E7D32; font-weight: 600;">✓ Grounded (${Math.round((data.confidence || 0.95)*100)}% Match)</span>`;
    }

    const personaLabels = {
      professor: "🎓 Professor",
      feynman: "💡 Feynman",
      socratic: "🏛️ Socratic",
      cram: "⚡ Exam Cram"
    };
    const personaTag = data.persona ? `<span style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--accent); background: var(--accent-muted); border: 1px solid var(--border); padding: 0.15rem 0.55rem; border-radius: var(--radius-sm); letter-spacing: 0.05em;">${personaLabels[data.persona] || data.persona}</span>` : '';

    meta.innerHTML = `
      <span class="bot-avatar-badge">🧠 SynapseLearn AI</span>
      ${personaTag}
      <span>•</span>
      ${statusBadge}
    `;

    const body = document.createElement('div');
    body.innerHTML = this.formatMarkdown(data.answer);

    // Citations Chips Container
    if (data.modal_data && data.modal_data.length) {
      const citationsBox = document.createElement('div');
      citationsBox.className = 'citation-chips-container';

      const label = document.createElement('span');
      label.style.fontFamily = 'var(--font-mono)';
      label.style.fontSize = '0.72rem';
      label.style.letterSpacing = '0.08em';
      label.style.textTransform = 'uppercase';
      label.style.color = 'var(--text-muted)';
      label.style.marginRight = '0.5rem';
      label.innerText = 'Deep Source Proof:';
      citationsBox.appendChild(label);

      data.modal_data.forEach(unit => {
        const chip = document.createElement('button');
        chip.className = 'citation-chip';
        
        let icon = '📖';
        if (unit.source_type === 'video') icon = '🎥';
        else if (unit.source_type === 'slide') icon = '🖼️';

        chip.innerHTML = `${icon} ${unit.citation_label}`;
        chip.title = `Click to inspect original ${unit.source_type} source`;
        chip.addEventListener('click', () => {
          window.openCitationModal(unit.id);
        });
        citationsBox.appendChild(chip);
      });

      body.appendChild(citationsBox);
    }

    bubble.appendChild(meta);
    bubble.appendChild(body);
    this.messagesContainer.appendChild(bubble);
    this.scrollToBottom();
  },

  appendLoadingBubble(id) {
    const bubble = document.createElement('div');
    bubble.id = id;
    bubble.className = 'message-bubble bot-msg';
    bubble.innerHTML = `
      <div class="message-meta"><span class="bot-avatar-badge">🧠 SynapseLearn AI</span></div>
      <div style="display: flex; gap: 6px; align-items: center; padding: 0.5rem 0;">
        <span style="font-size: 0.9rem; color: var(--text-muted); font-style: italic;">Retrieving multimodal sources & verifying grounding...</span>
      </div>
    `;
    this.messagesContainer.appendChild(bubble);
    this.scrollToBottom();
  },

  removeLoadingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  },

  formatMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 5px; border-radius: 4px; font-family: monospace;">$1</code>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
    return html;
  },

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }
};
