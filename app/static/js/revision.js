/**
 * Smart Revision Suite Module:
 * Flashcards with Leitner system, Topic Cheat-Sheets, Study Schedule Planner, and Audio Briefs.
 */

window.RevisionModule = {
  flashcards: [],
  currentCardIdx: 0,
  isFlipped: false,

  async init() {
    await this.loadFlashcards();
    this.setupFlashcardControls();
    this.setupSchedulePlanner();
    this.loadCheatSheet('topic-1');
  },

  async loadFlashcards() {
    try {
      const res = await fetch('/api/revision/flashcards');
      if (res.ok) {
        this.flashcards = await res.json();
        this.renderCurrentFlashcard();
      }
    } catch (err) {
      console.error('Failed to load flashcards:', err);
    }
  },

  renderCurrentFlashcard() {
    const cardEl = document.getElementById('revisionFlashcard');
    if (!cardEl || !this.flashcards.length) return;

    const card = this.flashcards[this.currentCardIdx];
    this.isFlipped = false;

    const boxLabel = `Leitner Box ${card.box}`;
    const indicatorEl = document.getElementById('fcIndexIndicator');
    if (indicatorEl) {
      indicatorEl.innerText = `Card ${this.currentCardIdx + 1} of ${this.flashcards.length} • ${card.topic_name}`;
    }

    cardEl.innerHTML = `
      <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted);">
        <span style="font-family: var(--font-mono); font-weight: 600; color: var(--accent); letter-spacing: 0.08em; text-transform: uppercase;">${boxLabel}</span>
        <span style="font-style: italic;">(Click to flip card)</span>
      </div>

      <div class="flashcard-content" id="fcContentText">
        ${card.front}
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 0.75rem;">
        <span style="font-family: var(--font-mono); font-size: 0.75rem;">📌 ${card.citation}</span>
        <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent); font-weight: 600;">🔄 Flip to view formula & proof</span>
      </div>
    `;
  },

  flipCard() {
    if (!this.flashcards.length) return;
    const card = this.flashcards[this.currentCardIdx];
    this.isFlipped = !this.isFlipped;

    const contentEl = document.getElementById('fcContentText');
    if (!contentEl) return;

    if (this.isFlipped) {
      contentEl.innerHTML = `
        <div style="color: var(--text-main); font-size: 1.05rem; line-height: 1.7; text-align: left;">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); margin-bottom: 0.5rem;">Answer & Derivation:</div>
          ${card.back}
        </div>
      `;
    } else {
      contentEl.innerHTML = card.front;
    }
  },

  setupFlashcardControls() {
    const cardEl = document.getElementById('revisionFlashcard');
    if (cardEl) {
      cardEl.addEventListener('click', () => this.flipCard());
    }

    const prevBtn = document.getElementById('prevFcBtn');
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (this.currentCardIdx > 0) {
          this.currentCardIdx--;
          this.renderCurrentFlashcard();
        }
      });
    }

    const nextBtn = document.getElementById('nextFcBtn');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (this.currentCardIdx < this.flashcards.length - 1) {
          this.currentCardIdx++;
          this.renderCurrentFlashcard();
        }
      });
    }

    const aiFcBtn = document.getElementById('aiGenerateFlashcardsBtn');
    if (aiFcBtn) {
      aiFcBtn.addEventListener('click', () => this.generateAIFlashcards());
    }
  },

  async generateAIFlashcards() {
    const aiBtn = document.getElementById('aiGenerateFlashcardsBtn');
    if (aiBtn) {
      aiBtn.disabled = true;
      aiBtn.innerText = '✨ Synthesizing Cards...';
    }

    try {
      const res = await fetch('/api/revision/ai-flashcards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic_id: 'topic-1',
          num_cards: 3,
          api_key_override: AppState.apiKey || null
        })
      });

      if (!res.ok) throw new Error('Failed to synthesize flashcards');
      const newCards = await res.json();
      this.flashcards = newCards.concat(this.flashcards);
      this.currentCardIdx = 0;
      this.renderCurrentFlashcard();
      alert(`✨ Synthesized ${newCards.length} novel AI Leitner flashcards!`);
    } catch (err) {
      alert('Failed to synthesize flashcards: ' + err.message);
    } finally {
      if (aiBtn) {
        aiBtn.disabled = false;
        aiBtn.innerText = '✨ AI Synthesize Flashcards';
      }
    }
  },

  async loadCheatSheet(topicId) {
    try {
      const res = await fetch(`/api/revision/cheat-sheet/${topicId}`);
      if (!res.ok) return;
      const sheet = await res.json();

      const container = document.getElementById('cheatSheetContent');
      if (!container) return;

      container.innerHTML = `
        <div style="margin-bottom: 1.5rem; padding-bottom: 0.85rem; border-bottom: 1px solid var(--border);">
          <h3 style="font-family: var(--font-serif); font-size: 1.25rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.35rem;">
            ${sheet.title}
          </h3>
          <div style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent);">
            Citations: ${sheet.citations.join(' • ')}
          </div>
        </div>

        <div style="margin-bottom: 1.5rem;">
          <h4 style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; color: var(--accent); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.65rem;">
            Key Mathematical Formulas:
          </h4>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            ${sheet.key_formulas.map(f => `
              <div style="background: var(--bg-secondary); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: 0.88rem; color: var(--text-main);">
                ${f}
              </div>
            `).join('')}
          </div>
        </div>

        <div>
          <h4 style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.65rem;">
            Core Takeaways & Common Pitfalls:
          </h4>
          <ul style="padding-left: 1.25rem; font-size: 0.92rem; color: var(--text-main); line-height: 1.7;">
            ${sheet.core_insights.map(i => `<li>${i}</li>`).join('')}
          </ul>
        </div>
      `;

      // Update audio brief script
      const audioBriefRes = await fetch(`/api/revision/audio-brief/${topicId}`);
      if (audioBriefRes.ok) {
        const audioData = await audioBriefRes.json();
        this.currentAudioBrief = audioData;
      }
    } catch (err) {
      console.error('Failed to load cheat sheet:', err);
    }
  },

  playAudioBrief() {
    if (!this.currentAudioBrief) return;
    speakText(this.currentAudioBrief.script);
  },

  setupSchedulePlanner() {
    const planBtn = document.getElementById('generateScheduleBtn');
    if (!planBtn) return;

    planBtn.addEventListener('click', async () => {
      const daysInput = document.getElementById('scheduleDaysInput');
      const days = daysInput ? parseInt(daysInput.value) : 7;

      try {
        const res = await fetch('/api/revision/study-schedule', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            days_until_exam: days,
            hours_per_day: 2.0
          })
        });

        if (res.ok) {
          const schedule = await res.json();
          this.renderSchedule(schedule);
        }
      } catch (err) {
        alert('Failed to generate schedule: ' + err.message);
      }
    });
  },

  renderSchedule(schedule) {
    const container = document.getElementById('studyScheduleTableBody');
    if (!container) return;
    container.innerHTML = '';

    schedule.forEach(dayItem => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 700; font-family: var(--font-serif);">Day ${dayItem.day} (${dayItem.date})</td>
        <td>
          <span style="font-weight: 600; color: ${dayItem.is_weak_topic ? '#B71C1C' : 'var(--text-main)'};">
            ${dayItem.topic_title}
          </span>
          ${dayItem.is_weak_topic ? '<span style="font-family: var(--font-mono); font-size: 0.7rem; background: rgba(183, 28, 28, 0.08); color: #B71C1C; border: 1px solid rgba(183, 28, 28, 0.2); padding: 2px 7px; border-radius: var(--radius-sm); margin-left: 6px; letter-spacing: 0.05em;">Priority Weak Area</span>' : ''}
        </td>
        <td style="font-family: var(--font-mono);">${dayItem.allocated_hours} hrs</td>
        <td>
          <ul style="padding-left: 1rem; font-size: 0.85rem; color: var(--text-muted); line-height: 1.5;">
            ${dayItem.tasks.map(t => `<li>${t}</li>`).join('')}
          </ul>
        </td>
      `;
      container.appendChild(tr);
    });
  }
};
