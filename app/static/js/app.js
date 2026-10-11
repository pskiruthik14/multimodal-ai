/**
 * SynapseLearn AI: Global State and Main Application Controller
 */

const AppState = {
  activeTab: 'chat',
  bilingualMode: false,
  voiceMode: false,
  apiKey: localStorage.getItem('gemini_api_key') || '',
  activeStudentId: 'student_default',
  activePersona: 'professor',
  courseData: null,
  masteryData: null
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  initNavigation();
  initHeaderControls();
  initModals();
  await loadCourseData();
  await loadMasteryData();

  // Default tab initialize
  if (window.ChatModule) window.ChatModule.init();
  if (window.KnowledgeMapModule) window.KnowledgeMapModule.init();
  if (window.IngestionModule) window.IngestionModule.init();
});

function initNavigation() {
  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  AppState.activeTab = tabId;

  // Update nav buttons
  document.querySelectorAll('.nav-tab-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });

  // Update tab panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.id === `tab-${tabId}`);
  });

  // Smooth scroll to top of main container for aligned reading experience
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Trigger tab-specific loaders
  if (tabId === 'map' && window.KnowledgeMapModule) {
    window.KnowledgeMapModule.onTabActivated();
  } else if (tabId === 'assessment' && window.AssessmentModule) {
    window.AssessmentModule.init();
  } else if (tabId === 'analytics' && window.LearnerModelModule) {
    window.LearnerModelModule.loadAnalytics();
  } else if (tabId === 'revision' && window.RevisionModule) {
    window.RevisionModule.init();
  } else if (tabId === 'eval' && window.EvaluationModule) {
    window.EvaluationModule.init();
  } else if (tabId === 'ingestion' && window.IngestionModule) {
    window.IngestionModule.init();
  }
}

function initHeaderControls() {
  // Persona Selector Buttons
  document.querySelectorAll('.persona-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.persona-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      AppState.activePersona = btn.getAttribute('data-persona');
      const personaNames = {
        professor: "Professor Mode",
        feynman: "Feynman ELI5 Mode",
        socratic: "Socratic Tutor Mode",
        cram: "Exam Cram Mode"
      };
      if (AppState.voiceMode) {
        speakText(`Switched to ${personaNames[AppState.activePersona] || 'Persona'}`);
      }
    });
  });

  // Hinglish Mode Toggle
  const hinglishBtn = document.getElementById('hinglishToggleBtn');
  if (hinglishBtn) {
    hinglishBtn.addEventListener('click', () => {
      AppState.bilingualMode = !AppState.bilingualMode;
      hinglishBtn.classList.toggle('active-toggle', AppState.bilingualMode);
      hinglishBtn.innerHTML = AppState.bilingualMode 
        ? '🇮🇳 Hinglish Active' 
        : '🌐 Hinglish Mode';
    });
  }

  // Voice Tutor Toggle
  const voiceBtn = document.getElementById('voiceToggleBtn');
  if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
      AppState.voiceMode = !AppState.voiceMode;
      voiceBtn.classList.toggle('voice-active', AppState.voiceMode);
      voiceBtn.innerHTML = AppState.voiceMode 
        ? '🎙️ Voice Active' 
        : '🎙️ Voice Tutor';
      if (AppState.voiceMode) {
        speakText("Voice tutoring activated. I will narrate grounded explanations for you.");
      }
    });
  }

  // Settings / API Key Button
  const settingsBtn = document.getElementById('settingsBtn');
  if (settingsBtn) {
    settingsBtn.addEventListener('click', () => {
      openSettingsModal();
    });
  }
}

async function loadCourseData() {
  try {
    const res = await fetch('/api/course');
    if (res.ok) {
      AppState.courseData = await res.json();
      console.log('Course loaded:', AppState.courseData.name);
    }
  } catch (err) {
    console.error('Failed to load course data:', err);
  }
}

async function loadMasteryData() {
  try {
    const res = await fetch('/api/learner/mastery');
    if (res.ok) {
      AppState.masteryData = await res.json();
    }
  } catch (err) {
    console.error('Failed to load mastery data:', err);
  }
}

// Global Text-to-Speech (TTS)
function speakText(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  
  // Clean markdown artifacts for clean pronunciation
  const clean = text.replace(/[*#_`>$\\]/g, ' ').replace(/\(https?:[^\)]+\)/g, '').substring(0, 300);
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

// Modal Controllers
function initModals() {
  const closeBtns = document.querySelectorAll('.modal-close-btn');
  closeBtns.forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.remove('open'));
    });
  });

  // Close on clicking backdrop
  document.querySelectorAll('.modal-backdrop').forEach(m => {
    m.addEventListener('click', (e) => {
      if (e.target === m) m.classList.remove('open');
    });
  });
}

function openSettingsModal() {
  const modal = document.getElementById('settingsModal');
  const input = document.getElementById('geminiApiKeyInput');
  if (input) input.value = AppState.apiKey;
  if (modal) modal.classList.add('open');
}

function saveSettings() {
  const input = document.getElementById('geminiApiKeyInput');
  if (input) {
    AppState.apiKey = input.value.trim();
    localStorage.setItem('gemini_api_key', AppState.apiKey);
  }
  document.getElementById('settingsModal').classList.remove('open');
  alert('Settings saved! Custom Gemini key will be used for queries.');
}

// Deep Citation Modal Opener
window.openCitationModal = async function(unitId) {
  const modal = document.getElementById('citationModal');
  const body = document.getElementById('citationModalBody');
  const title = document.getElementById('citationModalTitle');

  body.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading source excerpt...</div>';
  modal.classList.add('open');

  try {
    const res = await fetch(`/api/units/${unitId}`);
    if (!res.ok) throw new Error('Unit not found');
    const data = await res.json();

    title.innerHTML = `📌 Source Grounding: ${data.citation_label}`;

    let mediaHtml = '';
    if (data.source_type === 'video') {
      mediaHtml = `
        <div class="citation-viewer-media" style="padding: 1.5rem; text-align: center; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: 1.25rem;">
          <div style="font-size: 2.5rem; margin-bottom: 0.5rem; color: var(--accent);">🎥</div>
          <div style="font-family: var(--font-serif); font-weight: 700; font-size: 1.15rem; color: var(--text-main);">Lecture Video Playback</div>
          <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Timestamp: ${data.timestamp_formatted || '00:00'}</div>
          <div style="margin-top: 1rem; width: 75%; background: var(--border); height: 6px; border-radius: 3px; overflow: hidden; margin-left: auto; margin-right: auto;">
            <div style="background: var(--accent); width: 60%; height: 100%;"></div>
          </div>
          <div style="margin-top: 0.75rem; font-size: 0.78rem; color: var(--text-muted);">(Synchronized high-res lecture stream at verified timestamp offset)</div>
        </div>
      `;
    } else if (data.source_type === 'slide') {
      mediaHtml = `
        <div class="citation-viewer-media" style="padding: 1.25rem; background: #FFFFFF; border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 0.65rem; font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">
            <span>🖼️ Slide Visual Preview (Slide #${data.slide_number})</span>
            <span style="color: #2E7D32; font-weight: 600;">● High-Res Vector Extracted</span>
          </div>
          ${data.diagram_svg || '<div style="padding: 2rem; color: var(--text-muted);">Visual diagram extracted from presentation deck.</div>'}
        </div>
      `;
    } else {
      mediaHtml = `
        <div class="citation-viewer-media" style="padding: 1.5rem; background: #FFFFFF; border: 1px solid var(--border); border-radius: var(--radius-sm); text-align: left; margin-bottom: 1.25rem;">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); margin-bottom: 0.5rem;">
            📖 Textbook Page Callout (Page ${data.page_number})
          </div>
          ${data.diagram_svg ? data.diagram_svg : ''}
        </div>
      `;
    }

    body.innerHTML = `
      ${mediaHtml}
      <div style="background: var(--bg-secondary); padding: 1.35rem; border-radius: var(--radius-sm); border: 1px solid var(--border); border-left: 3px solid var(--accent); margin-bottom: 1.25rem;">
        <div style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
          Verified Course Text Excerpt
        </div>
        <p style="font-family: var(--font-serif); font-size: 1.05rem; line-height: 1.7; color: var(--text-main); font-style: italic;">
          "${data.text_content}"
        </p>
      </div>

      ${data.visual_description ? `
        <div style="background: var(--bg-secondary); border: 1px solid var(--border); border-left: 3px solid var(--accent); padding: 1rem 1.25rem; border-radius: var(--radius-sm); margin-bottom: 1.25rem;">
          <div style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); margin-bottom: 0.35rem;">
            Extracted Figure / Diagram Information:
          </div>
          <div style="font-size: 0.9rem; color: var(--text-main); line-height: 1.6;">${data.visual_description}</div>
        </div>
      ` : ''}

      ${data.equations && data.equations.length ? `
        <div style="background: var(--bg-secondary); border: 1px solid var(--border); padding: 1rem 1.25rem; border-radius: var(--radius-sm);">
          <div style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); margin-bottom: 0.5rem;">Mathematical Formulations in Source:</div>
          ${data.equations.map(eq => `<div style="font-family: var(--font-mono); font-size: 0.88rem; color: var(--text-main); margin-bottom: 0.35rem;">$ ${eq} $</div>`).join('')}
        </div>
      ` : ''}
    `;
  } catch (err) {
    body.innerHTML = `<div style="color: #B71C1C; padding: 1rem;">Failed to load citation: ${err.message}</div>`;
  }
};

// ==================== ADVANCED AI FEATURE MODALS ====================

// 1. AI Misconception Clinic Modal
window.openMisconceptionModal = async function(misconception, topicName) {
  const modal = document.getElementById('remediationModal');
  const body = document.getElementById('remediationModalBody');
  const title = document.getElementById('remediationModalTitle');

  body.innerHTML = '<div style="text-align: center; padding: 2.5rem; color: var(--text-muted);">Analyzing misconception cognitive roots...</div>';
  modal.classList.add('open');

  try {
    const res = await fetch('/api/ai/remediate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        misconception: misconception || 'Conceptual confusion in optimization',
        topic_name: topicName || 'CS229 Foundations',
        api_key_override: AppState.apiKey || null
      })
    });
    if (!res.ok) throw new Error('Failed to run remediation clinic');
    const data = await res.json();

    title.innerText = `🩺 AI Clinic: ${data.title}`;

    const pc = data.practice_check;
    body.innerHTML = `
      <div style="background: rgba(183, 28, 28, 0.04); border: 1px solid rgba(183, 28, 28, 0.15); border-left: 3px solid var(--danger); padding: 1.1rem 1.25rem; border-radius: var(--radius-sm); margin-bottom: 1.25rem;">
        <div style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; color: #7F1D1D; text-transform: uppercase; letter-spacing: 0.08em;">Diagnosed Cognitive Slip:</div>
        <div style="font-size: 0.95rem; color: #7F1D1D; margin-top: 0.25rem; font-weight: 500;">${misconception}</div>
      </div>

      <div style="line-height: 1.7; font-size: 0.95rem; color: var(--text-main); margin-bottom: 1.25rem;">
        ${data.explanation.replace(/\n\n/g, '<br><br>')}
      </div>

      <div style="background: var(--bg-secondary); border: 1px solid var(--border); border-left: 3px solid var(--accent); padding: 1rem 1.25rem; border-radius: var(--radius-sm); margin-bottom: 1.25rem;">
        <div style="font-family: var(--font-mono); font-weight: 600; color: var(--accent); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em;">💡 Key Memory Rule:</div>
        <div style="color: var(--text-main); font-size: 0.92rem; margin-top: 0.25rem; line-height: 1.6;">${data.key_takeaway}</div>
      </div>

      ${pc ? `
        <div class="practice-check-box" style="background: var(--bg-secondary); border: 1px solid var(--border); padding: 1.25rem; border-radius: var(--radius-sm);">
          <div style="font-family: var(--font-mono); font-weight: 600; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
            🎯 Check Your Understanding:
          </div>
          <div style="font-size: 0.92rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.85rem;">${pc.question}</div>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            ${pc.options.map(opt => `
              <label style="display: flex; align-items: center; gap: 0.65rem; background: var(--bg-card); border: 1px solid var(--border); padding: 0.65rem 0.95rem; border-radius: var(--radius-sm); cursor: pointer; color: var(--text-main); font-size: 0.9rem;">
                <input type="radio" name="practice_opt" value="${opt[0]}">
                <span>${opt}</span>
              </label>
            `).join('')}
          </div>
          <div style="margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <button class="btn-primary" style="font-size: 0.82rem; padding: 0.45rem 1rem;" onclick="window.checkPracticeAnswer('${pc.correct}', '${pc.explanation.replace(/'/g, "\\'")}')">
              Verify Answer
            </button>
            <div id="practiceResultText" style="font-size: 0.88rem; font-weight: 600;"></div>
          </div>
        </div>
      ` : ''}
    `;
  } catch (err) {
    body.innerHTML = `<div style="color: #B71C1C; padding: 1rem;">Clinic error: ${err.message}</div>`;
  }
};

window.checkPracticeAnswer = function(correctLetter, explanation) {
  const selected = document.querySelector('input[name="practice_opt"]:checked');
  const resDiv = document.getElementById('practiceResultText');
  if (!selected) {
    alert('Please pick an option first!');
    return;
  }
  if (selected.value === correctLetter) {
    resDiv.innerHTML = `<span style="color: #2E7D32;">✓ Correct! ${explanation}</span>`;
  } else {
    resDiv.innerHTML = `<span style="color: #B71C1C;">✗ Not quite. ${explanation}</span>`;
  }
};

// 2. AI Architecture Comparison Modal
window.openComparisonModal = async function(key = 'optimizers') {
  const modal = document.getElementById('comparisonModal');
  modal.classList.add('open');
  await window.loadComparison(key);
};

window.loadCustomComparison = async function() {
  const input = document.getElementById('customCompareInput');
  const query = input ? input.value.trim() : '';
  if (!query) {
    alert('Please enter concepts to compare (e.g., "AdamW vs Lion" or "CNN vs ViT")');
    return;
  }
  await window.loadComparison(query);
};

window.loadComparison = async function(key) {
  const body = document.getElementById('comparisonModalBody');
  const title = document.getElementById('comparisonModalTitle');

  // Update active pill button if matching
  document.querySelectorAll('#comparisonModal .action-pill-btn').forEach(btn => {
    const onclickStr = btn.getAttribute('onclick') || '';
    btn.classList.toggle('active-toggle', onclickStr.includes(key));
  });

  body.innerHTML = '<div style="text-align: center; padding: 2.5rem; color: var(--text-muted);"><div style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--accent);">⚖️</div><div>Synthesizing dynamic AI comparison matrix...</div></div>';

  try {
    const res = await fetch('/api/ai/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        comparison_key: key,
        api_key_override: AppState.apiKey || null
      })
    });
    if (!res.ok) throw new Error('Failed to load comparison');
    const data = await res.json();

    title.innerText = `⚖️ ${data.title}`;

    body.innerHTML = `
      <table class="custom-table" style="width: 100%;">
        <thead>
          <tr>
            ${data.headers.map(h => `<th>${h}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${data.rows.map(row => `
            <tr>
              ${row.map((cell, idx) => `
                <td style="${idx === 0 ? 'font-family: var(--font-mono); font-weight: 600; color: var(--accent);' : ''}">
                  ${cell}
                </td>
              `).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
      <div style="margin-top: 1.25rem; font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted);">
        <strong>Grounding Sources:</strong> ${data.citations ? data.citations.join(' • ') : 'CS229 Foundations'}
      </div>
    `;
  } catch (err) {
    body.innerHTML = `<div style="color: #B71C1C; padding: 1rem;">Comparison error: ${err.message}</div>`;
  }
};

// 3. AI Multimodal Diagram Explainer
window.openDiagramExplainer = async function(unitId = 'unit-tb-01') {
  const modal = document.getElementById('diagramExplainerModal');
  const body = document.getElementById('diagramExplainerBody');
  const title = document.getElementById('diagramExplainerTitle');
  const select = document.getElementById('diagramSelect');

  if (select && unitId) {
    select.value = unitId;
  }

  body.innerHTML = '<div style="text-align: center; padding: 2.5rem; color: var(--text-muted);"><div style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--accent);">🔍</div><div>Analyzing visual diagram elements & tensor vector flows with AI...</div></div>';
  modal.classList.add('open');

  try {
    const res = await fetch('/api/ai/diagram-explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        unit_id: unitId,
        api_key_override: AppState.apiKey || null
      })
    });
    if (!res.ok) throw new Error('Failed to analyze diagram');
    const data = await res.json();

    title.innerText = `🔍 AI Explainer: ${data.title}`;

    body.innerHTML = `
      <div style="background: var(--bg-secondary); border: 1px solid var(--border); border-left: 3px solid var(--accent); padding: 0.85rem 1.15rem; border-radius: var(--radius-sm); margin-bottom: 1.25rem;">
        <span style="font-family: var(--font-mono); font-weight: 600; color: var(--accent); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em;">Architecture Type:</span>
        <span style="color: var(--text-main); margin-left: 0.5rem; font-size: 0.92rem; font-weight: 600;">${data.architecture_type}</span>
      </div>

      <div style="margin-bottom: 1.25rem;">
        <h4 style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 0.65rem;">Visual Diagram Components & Vectors:</h4>
        <ul style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.92rem; line-height: 1.6; padding-left: 1.25rem; color: var(--text-main);">
          ${data.visual_elements.map(el => `<li>${el}</li>`).join('')}
        </ul>
      </div>

      <div style="background: var(--bg-secondary); border: 1px solid var(--border); border-left: 3px solid var(--accent); padding: 1rem 1.25rem; border-radius: var(--radius-sm);">
        <div style="font-family: var(--font-mono); font-weight: 600; color: var(--accent); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.35rem;">Mathematical Core Takeaway:</div>
        <div style="color: var(--text-main); font-size: 0.92rem; line-height: 1.6;">${data.mathematical_takeaway}</div>
      </div>

      <div style="margin-top: 1rem; font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted); text-align: right;">
        📍 Citation: ${data.citation}
      </div>
    `;
  } catch (err) {
    body.innerHTML = `<div style="color: #B71C1C; padding: 1rem;">Explainer error: ${err.message}</div>`;
  }
};

