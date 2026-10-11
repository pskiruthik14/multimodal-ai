/**
 * Learner Model & Analytics Module:
 * Renders Bayesian Knowledge Tracing (BKT) per-topic mastery,
 * Item Response Theory (IRT) theta, forgetting curve retention, and diagnostic intake onboarding.
 */

window.LearnerModelModule = {
  async init() {
    await this.loadAnalytics();
    this.setupIntakeModal();
  },

  async loadAnalytics() {
    try {
      // 1. Fetch BKT mastery
      const resMastery = await fetch('/api/learner/mastery');
      if (resMastery.ok) {
        const data = await resMastery.json();
        this.renderMasteryWidgets(data);
      }

      // 2. Fetch Forgetting curve
      const resForgetting = await fetch('/api/learner/forgetting-curve');
      if (resForgetting.ok) {
        const fData = await resForgetting.json();
        this.renderForgettingSchedule(fData.schedule);
      }
    } catch (err) {
      console.error('Failed to load learner analytics:', err);
    }
  },

  renderMasteryWidgets(data) {
    // Stats Summary
    const thetaEl = document.getElementById('statIrtTheta');
    if (thetaEl) thetaEl.innerText = (data.ability_theta >= 0 ? '+' : '') + data.ability_theta;

    const accEl = document.getElementById('statAccuracy');
    if (accEl) accEl.innerText = `${Math.round((data.accuracy || 0) * 100)}%`;

    const masterCountEl = document.getElementById('statMasteredCount');
    if (masterCountEl) masterCountEl.innerText = `${data.mastered_topics_count} / 6`;

    const weakCountEl = document.getElementById('statWeakCount');
    if (weakCountEl) weakCountEl.innerText = `${data.weak_topics_count}`;

    // Per-Topic BKT Bars
    const container = document.getElementById('bktTopicBars');
    if (!container) return;
    container.innerHTML = '';

    const details = data.topic_details || {};
    Object.values(details).forEach(topic => {
      const row = document.createElement('div');
      row.className = 'mastery-row';

      const pct = Math.round(topic.p_mastery * 100);
      let barColor = '#8C8883';
      let statusText = 'Learning';
      if (topic.p_mastery >= 0.85) {
        barColor = '#2E7D32';
        statusText = 'Mastered';
      } else if (topic.p_mastery >= 0.50) {
        barColor = '#B8860B';
        statusText = 'Developing';
      }

      row.innerHTML = `
        <div class="mastery-header">
          <span>${topic.topic_name}</span>
          <span style="color: ${barColor}; font-family: var(--font-mono); font-weight: 600;">${pct}% (${statusText})</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%; background: ${barColor};"></div>
        </div>
      `;
      container.appendChild(row);
    });
  },

  renderForgettingSchedule(schedule) {
    const container = document.getElementById('forgettingCurveTableBody');
    if (!container) return;
    container.innerHTML = '';

    schedule.forEach(item => {
      const tr = document.createElement('tr');
      const retPct = Math.round(item.retention * 100);
      let urgencyColor = '#2E7D32';
      if (item.retention < 0.50) urgencyColor = '#B71C1C';
      else if (item.retention < 0.75) urgencyColor = '#B8860B';

      tr.innerHTML = `
        <td style="font-weight: 600;">${item.topic_id}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div class="progress-track" style="width: 80px; height: 6px;">
              <div class="progress-fill" style="width: ${retPct}%; background: ${urgencyColor};"></div>
            </div>
            <span style="font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600; color: ${urgencyColor};">${retPct}%</span>
          </div>
        </td>
        <td>${item.last_studied_days_ago} days ago</td>
        <td>${item.review_count} reviews</td>
        <td style="color: ${urgencyColor}; font-weight: 600; font-family: var(--font-mono); font-size: 0.8rem;">${item.urgency}</td>
        <td>
          <button class="btn-outline" style="font-size: 0.75rem; padding: 0.35rem 0.75rem;" onclick="window.startTopicQuiz('${item.topic_id}')">
            Review Now
          </button>
        </td>
      `;
      container.appendChild(tr);
    });
  },

  setupIntakeModal() {
    const intakeBtn = document.getElementById('startIntakeBtn');
    const modal = document.getElementById('intakeModal');
    if (intakeBtn && modal) {
      intakeBtn.addEventListener('click', () => {
        modal.classList.add('open');
      });
    }

    const resetBtn = document.getElementById('resetStudentModelBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', async () => {
        if (!confirm('Reset student learner model back to initial uncalibrated prior?')) return;
        await fetch('/api/learner/reset', { method: 'POST' });
        await this.loadAnalytics();
        if (window.KnowledgeMapModule) window.KnowledgeMapModule.render();
        alert('Learner model reset.');
      });
    }
  }
};

window.submitDiagnosticIntake = async function() {
  const levelSelect = document.getElementById('intakeLevelSelect');
  const level = levelSelect ? levelSelect.value : 'intermediate';

  // Read screener answers
  let score = 0;
  const q1 = document.querySelector('input[name="diag-ans-diag-01"]:checked');
  const q2 = document.querySelector('input[name="diag-ans-diag-02"]:checked');
  const q3 = document.querySelector('input[name="diag-ans-diag-03"]:checked');

  if (q1 && q1.value === 'A') score += 1;
  if (q2 && q2.value === 'A') score += 1;
  if (q3 && q3.value === 'A') score += 1;

  try {
    const res = await fetch('/api/learner/intake', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        self_reported_level: level,
        diagnostic_score: score
      })
    });

    if (res.ok) {
      document.getElementById('intakeModal').classList.remove('open');
      await window.LearnerModelModule.loadAnalytics();
      if (window.KnowledgeMapModule) window.KnowledgeMapModule.render();
      alert(`Onboarding completed! Calibrated initial ability theta based on ${level} background and score ${score}/3.`);
    }
  } catch (err) {
    alert('Intake submission failed: ' + err.message);
  }
};
