/**
 * Adaptive Assessment Studio Module:
 * Generates verified quizzes, records answers, and renders misconception diagnostic reports.
 */

window.AssessmentModule = {
  currentQuestions: [],
  selectedAnswers: {},

  init() {
    this.quizContainer = document.getElementById('quizQuestionsArea');
    this.reportContainer = document.getElementById('quizReportArea');
    this.generateBtn = document.getElementById('generateQuizBtn');
    this.aiGenerateBtn = document.getElementById('aiGenerateQuizBtn');
    this.submitBtn = document.getElementById('submitQuizBtn');

    if (this.generateBtn) {
      this.generateBtn.addEventListener('click', () => this.generateQuiz());
    }
    if (this.aiGenerateBtn) {
      this.aiGenerateBtn.addEventListener('click', () => this.generateAIQuiz());
    }
    if (this.submitBtn) {
      this.submitBtn.addEventListener('click', () => this.submitQuiz());
    }
  },

  async generateAIQuiz() {
    const topicSelect = document.getElementById('quizTopicSelect');
    const diffSelect = document.getElementById('quizDifficultySelect');
    const numSelect = document.getElementById('quizNumQuestionsSelect');

    const topicId = (topicSelect && topicSelect.value !== 'all') ? topicSelect.value : 'topic-1';
    const difficulty = (diffSelect && diffSelect.value !== 'adaptive') ? diffSelect.value : 'medium';
    const numQuestions = numSelect ? parseInt(numSelect.value) : 3;

    this.quizContainer.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem; color: var(--accent);">✨</div>
        <div style="font-family: var(--font-serif); font-weight: 700; font-size: 1.25rem; color: var(--text-main);">Synthesizing Novel AI Questions...</div>
        <div style="font-size: 0.88rem; color: var(--text-muted); margin-top: 0.35rem;">Generating verified question keys, misconception distractors, and exact citations.</div>
      </div>
    `;
    this.reportContainer.style.display = 'none';
    this.submitBtn.style.display = 'none';

    try {
      const res = await fetch('/api/assessment/ai-generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic_id: topicId,
          difficulty: difficulty,
          num_questions: numQuestions,
          api_key_override: AppState.apiKey || null
        })
      });

      if (!res.ok) throw new Error('Failed to synthesize AI questions');
      const data = await res.json();
      this.currentQuestions = data.questions;
      this.selectedAnswers = {};
      this.renderQuestions();
    } catch (err) {
      this.quizContainer.innerHTML = `<div style="color: #ef4444; padding: 1rem;">AI Generation Error: ${err.message}</div>`;
    }
  },

  async generateQuizForTopic(topicId) {
    const topicSelect = document.getElementById('quizTopicSelect');
    if (topicSelect) topicSelect.value = topicId;
    await this.generateQuiz();
  },

  async generateQuiz() {
    const topicSelect = document.getElementById('quizTopicSelect');
    const diffSelect = document.getElementById('quizDifficultySelect');
    const numSelect = document.getElementById('quizNumQuestionsSelect');

    const topicId = topicSelect ? topicSelect.value : null;
    const difficulty = diffSelect && diffSelect.value !== 'adaptive' ? diffSelect.value : null;
    const numQuestions = numSelect ? parseInt(numSelect.value) : 3;

    this.quizContainer.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--accent);">⚙️</div>
        <div style="font-family: var(--font-serif); font-size: 1.15rem; color: var(--text-main);">Calibrating adaptive assessment & verifying novelty...</div>
      </div>
    `;
    this.reportContainer.style.display = 'none';
    this.submitBtn.style.display = 'none';

    try {
      const payload = {
        num_questions: numQuestions
      };
      if (topicId && topicId !== 'all') payload.topic_ids = [topicId];
      if (difficulty) payload.difficulty = difficulty;

      const res = await fetch('/api/assessment/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Failed to generate assessment');
      const data = await res.json();
      this.currentQuestions = data.questions;
      this.selectedAnswers = {};

      this.renderQuestions();
    } catch (err) {
      this.quizContainer.innerHTML = `<div style="color: #ef4444; padding: 1rem;">Error: ${err.message}</div>`;
    }
  },

  renderQuestions() {
    if (!this.currentQuestions.length) {
      this.quizContainer.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: var(--text-muted); font-size: 0.95rem;">
          No unattempted questions found for this topic scope. Reset history or expand scope!
        </div>
      `;
      return;
    }

    this.quizContainer.innerHTML = '';
    this.currentQuestions.forEach((q, idx) => {
      const card = document.createElement('div');
      card.className = 'question-card';
      card.id = `q-card-${q.id}`;

      let diffClass = 'diff-medium';
      if (q.difficulty === 'easy') diffClass = 'diff-easy';
      else if (q.difficulty === 'hard') diffClass = 'diff-hard';

      let inputHtml = '';
      if (q.type === 'mcq') {
        inputHtml = `
          <div class="mcq-options-list">
            ${q.options.map(opt => {
              const optLetter = opt[0];
              return `
                <label class="mcq-option-label" id="opt-lbl-${q.id}-${optLetter}">
                  <input type="radio" name="ans-${q.id}" value="${optLetter}" onchange="window.AssessmentModule.recordAnswer('${q.id}', '${optLetter}')">
                  <span>${opt}</span>
                </label>
              `;
            }).join('')}
          </div>
        `;
      } else if (q.type === 'numerical') {
        inputHtml = `
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Enter calculated numerical answer:
            </label>
            <input type="text" class="chat-input" placeholder="e.g. 32 or 1.61" style="max-width: 250px;" 
                   oninput="window.AssessmentModule.recordAnswer('${q.id}', this.value)">
          </div>
        `;
      } else {
        inputHtml = `
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Provide conceptual explanation:
            </label>
            <textarea class="chat-input" rows="3" placeholder="Explain the concept in your own words..."
                      style="border-radius: var(--radius-sm); width: 100%;"
                      oninput="window.AssessmentModule.recordAnswer('${q.id}', this.value)"></textarea>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="question-header">
          <div style="display: flex; align-items: center; gap: 0.65rem;">
            <span class="question-tag">Question ${idx + 1}</span>
            <span style="font-size: 0.82rem; color: var(--text-muted);">${q.topic_name}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.65rem;">
            <span class="difficulty-badge ${diffClass}">${q.difficulty.toUpperCase()}</span>
            <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #2E7D32; background: rgba(46, 125, 50, 0.08); border: 1px solid rgba(46, 125, 50, 0.2); padding: 0.2rem 0.55rem; border-radius: var(--radius-sm);">
              ✓ Cross-Model Verified
            </span>
          </div>
        </div>

        <div class="question-text">${q.question_text}</div>
        ${inputHtml}
      `;

      this.quizContainer.appendChild(card);
    });

    this.submitBtn.style.display = 'inline-flex';
  },

  recordAnswer(qId, val) {
    this.selectedAnswers[qId] = val;
    // Highlight selected radio option
    const card = document.getElementById(`q-card-${qId}`);
    if (card) {
      card.querySelectorAll('.mcq-option-label').forEach(lbl => {
        lbl.classList.toggle('selected', lbl.id === `opt-lbl-${qId}-${val}`);
      });
    }
  },

  async submitQuiz() {
    if (Object.keys(this.selectedAnswers).length < this.currentQuestions.length) {
      if (!confirm('You have not answered all questions. Submit anyway?')) return;
    }

    this.submitBtn.disabled = true;
    this.submitBtn.innerText = 'Evaluating Diagnostics...';

    try {
      const res = await fetch('/api/assessment/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: AppState.activeStudentId,
          answers: this.selectedAnswers
        })
      });

      if (!res.ok) throw new Error('Evaluation failed');
      const report = await res.json();

      this.renderDiagnosticReport(report);
      // Reload knowledge graph and learner analytics
      if (window.KnowledgeMapModule) window.KnowledgeMapModule.render();
      if (window.LearnerModelModule) window.LearnerModelModule.loadAnalytics();
    } catch (err) {
      alert('Failed to submit quiz: ' + err.message);
    } finally {
      this.submitBtn.disabled = false;
      this.submitBtn.innerText = 'Submit Quiz & Diagnose';
      this.submitBtn.style.display = 'none';
    }
  },

  renderDiagnosticReport(report) {
    this.reportContainer.style.display = 'block';

    // Highlight per-question feedback in the quiz cards
    report.results.forEach(res => {
      const card = document.getElementById(`q-card-${res.question_id}`);
      if (!card) return;

      const fb = document.createElement('div');
      fb.className = `feedback-box ${res.is_correct ? 'feedback-correct' : 'feedback-incorrect'}`;
      
      fb.innerHTML = `
        <div style="font-weight: 700; margin-bottom: 0.25rem;">
          ${res.is_correct ? '✓ Correct Answer!' : '✗ Incorrect Answer'}
        </div>
        <div style="margin-bottom: 0.4rem;">${res.solution_explanation}</div>
        <div style="font-size: 0.8rem; font-weight: 600; color: #a5b4fc;">
          📌 Grounding Source: ${res.citation_label}
        </div>
        ${res.misconception_diagnosed ? `
          <div class="misconception-callout">
            <div style="margin-bottom: 0.35rem;">⚠️ <strong>Diagnosed Misconception:</strong> ${res.misconception_diagnosed}</div>
            <button class="btn-outline" style="font-size: 0.75rem; padding: 0.25rem 0.65rem; border-color: rgba(239, 68, 68, 0.4); color: #fca5a5;" onclick="window.openMisconceptionModal('${res.misconception_diagnosed.replace(/'/g, "\\'")}', '${res.topic_name}')">
              🩺 Open AI Remediation Clinic
            </button>
          </div>
        ` : ''}
      `;
      card.appendChild(fb);
    });

    // Render Diagnostic Summary at top of report container
    this.reportContainer.innerHTML = `
      <div class="glass-card" style="border: 1px solid var(--border); border-top: 3px solid var(--accent); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; padding-bottom: 0.85rem; border-bottom: 1px solid var(--border);">
          <div>
            <h2 style="font-family: var(--font-serif); font-size: 1.35rem; font-weight: 700; color: var(--text-main);">📊 Post-Assessment Diagnostic Report</h2>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.2rem;">
              Adaptive Evaluation & Bayesian Knowledge Tracing Calibration
            </div>
          </div>
          <div style="text-align: right;">
            <div style="font-family: var(--font-serif); font-size: 2.2rem; font-weight: 700; color: ${report.accuracy_percentage >= 70 ? '#2E7D32' : '#B8860B'};">
              ${report.accuracy_percentage}%
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted);">
              Score: ${report.score} / ${report.total_questions}
            </div>
          </div>
        </div>

        <!-- Topic Breakdown -->
        <div style="margin-bottom: 1.5rem;">
          <h4 style="font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.65rem; color: var(--text-muted);">Topic Performance Breakdown:</h4>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.85rem;">
            ${Object.entries(report.topic_breakdown).map(([tid, stat]) => `
              <div style="background: var(--bg-secondary); padding: 0.85rem 1.1rem; border-radius: var(--radius-sm); border: 1px solid var(--border);">
                <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.25rem;">${stat.topic_name}</div>
                <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-muted);">
                  <span>Accuracy: ${Math.round(stat.accuracy * 100)}%</span>
                  <span>(${stat.correct}/${stat.total})</span>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Diagnosed Misconceptions Summary -->
        ${report.identified_misconceptions.length ? `
          <div style="margin-bottom: 1.5rem; background: rgba(183, 28, 28, 0.04); border: 1px solid rgba(183, 28, 28, 0.15); border-left: 3px solid var(--danger); padding: 1.1rem 1.35rem; border-radius: var(--radius-sm);">
            <h4 style="font-size: 0.92rem; font-weight: 700; color: #7F1D1D; margin-bottom: 0.4rem;">
              ⚠️ Identified Cognitive Misconceptions:
            </h4>
            <ul style="padding-left: 1.25rem; font-size: 0.9rem; color: #7F1D1D; line-height: 1.6;">
              ${report.identified_misconceptions.map(m => `
                <li><strong>${m.topic_name}:</strong> ${m.misconception}</li>
              `).join('')}
            </ul>
          </div>
        ` : '<div style="color: #2E7D32; font-size: 0.92rem; font-weight: 600; margin-bottom: 1.25rem;">✓ No critical conceptual misconceptions identified!</div>'}

        <!-- Prescribed Corrective Review Units -->
        ${report.recommended_review_units && report.recommended_review_units.length ? `
          <div>
            <h4 style="font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.65rem; color: var(--accent);">
              🎯 Prescribed Corrective Review Materials:
            </h4>
            <div style="display: flex; flex-direction: column; gap: 0.65rem;">
              ${report.recommended_review_units.map(unit => `
                <div style="display: flex; align-items: center; justify-content: space-between; background: var(--bg-secondary); border: 1px solid var(--border); border-left: 3px solid var(--accent); padding: 0.85rem 1.15rem; border-radius: var(--radius-sm);">
                  <div>
                    <span style="font-weight: 600; font-size: 0.88rem; color: var(--text-main);">${unit.title}</span>
                    <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); margin-left: 0.5rem;">(${unit.citation_label})</span>
                  </div>
                  <button class="btn-outline" style="font-size: 0.75rem; padding: 0.35rem 0.75rem;" onclick="window.openCitationModal('${unit.id}')">
                    Inspect Source
                  </button>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;

    this.reportContainer.scrollIntoView({ behavior: 'smooth' });
  }
};
