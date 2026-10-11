/**
 * Ingestion & Multimodal Knowledge Hub Module:
 * Synchronizes Course Materials across Video Timestamps, Textbook Pages, and Slide Decks.
 * Features live multi-field search, topic filtering, modality filtering, and interactive unit cards.
 */

window.IngestionModule = {
  currentUnits: [],
  activeFilter: 'all',
  activeTopic: 'all',
  searchQuery: '',
  isInitialized: false,

  async init() {
    await this.loadCourseUnits();

    if (!this.isInitialized) {
      this.setupUploadDropzone();
      this.setupFilterTabs();
      this.isInitialized = true;
    }
  },

  async loadCourseUnits() {
    try {
      const res = await fetch('/api/course');
      if (!res.ok) return;
      const data = await res.json();
      this.currentUnits = data.content_units || [];
      this.renderStatsStrip();
      this.renderUnits();
    } catch (err) {
      console.error('Failed to load course units:', err);
    }
  },

  renderStatsStrip() {
    const strip = document.getElementById('hubStatsStrip');
    if (!strip || !this.currentUnits.length) return;

    const total = this.currentUnits.length;
    const videos = this.currentUnits.filter(u => u.source_type === 'video').length;
    const textbooks = this.currentUnits.filter(u => u.source_type === 'textbook').length;
    const slides = this.currentUnits.filter(u => u.source_type === 'slide').length;
    const diagrams = this.currentUnits.filter(u => !!u.visual_description).length;
    const equations = this.currentUnits.filter(u => u.equations && u.equations.length > 0).length;

    strip.innerHTML = `
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: var(--radius-sm); text-align: center; box-shadow: var(--shadow-sm);">
        <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: var(--accent);">${total}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.15rem;">Total Units</div>
      </div>
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: var(--radius-sm); text-align: center; box-shadow: var(--shadow-sm);">
        <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: #1976D2;">${videos}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.15rem;">🎥 Video Units</div>
      </div>
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: var(--radius-sm); text-align: center; box-shadow: var(--shadow-sm);">
        <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: #388E3C;">${textbooks}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.15rem;">📖 Textbooks</div>
      </div>
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: var(--radius-sm); text-align: center; box-shadow: var(--shadow-sm);">
        <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: #F57C00;">${slides}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.15rem;">🖼️ Slide Decks</div>
      </div>
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: var(--radius-sm); text-align: center; box-shadow: var(--shadow-sm);">
        <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: #7B1FA2;">${diagrams}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.15rem;">🎨 Vector Diagrams</div>
      </div>
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: var(--radius-sm); text-align: center; box-shadow: var(--shadow-sm);">
        <div style="font-family: var(--font-mono); font-size: 1.35rem; font-weight: 700; color: #C2185B;">${equations}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.15rem;">∑ Formulations</div>
      </div>
    `;
  },

  setupFilterTabs() {
    const filterBtns = document.querySelectorAll('.source-filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active-toggle'));
        btn.classList.add('active-toggle');
        this.activeFilter = btn.getAttribute('data-filter') || 'all';
        this.renderUnits();
      });
    });
  },

  handleSearch() {
    const input = document.getElementById('knowledgeSearchInput');
    this.searchQuery = input ? input.value.trim().toLowerCase() : '';
    this.renderUnits();
  },

  handleTopicFilter(topicId) {
    this.activeTopic = topicId || 'all';
    this.renderUnits();
  },

  renderUnits() {
    const container = document.getElementById('knowledgeUnitsGrid');
    const badge = document.getElementById('knowledgeUnitsCountBadge');
    if (!container) return;

    let filtered = this.currentUnits;

    // 1. Modality filter
    if (this.activeFilter !== 'all') {
      filtered = filtered.filter(u => u.source_type === this.activeFilter);
    }

    // 2. Topic filter
    if (this.activeTopic !== 'all') {
      filtered = filtered.filter(u => u.topic_id === this.activeTopic);
    }

    // 3. Search query filter
    if (this.searchQuery) {
      filtered = filtered.filter(u => {
        const titleMatch = (u.title || '').toLowerCase().includes(this.searchQuery);
        const textMatch = (u.text_content || '').toLowerCase().includes(this.searchQuery);
        const citeMatch = (u.citation_label || '').toLowerCase().includes(this.searchQuery);
        const tagsMatch = (u.concept_tags || []).some(t => t.toLowerCase().includes(this.searchQuery));
        const eqMatch = (u.equations || []).some(eq => eq.toLowerCase().includes(this.searchQuery));
        return titleMatch || textMatch || citeMatch || tagsMatch || eqMatch;
      });
    }

    if (badge) {
      badge.innerText = `${filtered.length} of ${this.currentUnits.length} units`;
    }

    container.innerHTML = '';

    if (!filtered.length) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1.5rem; background: var(--bg-card); border: 1px dashed var(--border); border-radius: var(--radius-md);">
          <div style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--accent);">🔍</div>
          <div style="font-family: var(--font-serif); font-size: 1.15rem; font-weight: 700; color: var(--text-main);">No matching course content units found</div>
          <p style="font-size: 0.88rem; color: var(--text-muted); margin-top: 0.35rem; margin-bottom: 1.25rem;">
            Try clearing search keywords or switching topic and source filters.
          </p>
          <button class="btn-outline" style="font-size: 0.82rem; padding: 0.45rem 1rem;" onclick="window.IngestionModule.resetFilters()">
            ↺ Reset Filters
          </button>
        </div>
      `;
      return;
    }

    filtered.forEach(unit => {
      const card = document.createElement('div');
      card.className = 'glass-card';
      card.style.display = 'flex';
      card.style.flexDirection = 'column';
      card.style.justifyContent = 'space-between';
      card.style.borderTop = '3px solid var(--accent)';
      card.style.padding = '1.35rem';
      card.style.gap = '0.85rem';

      let icon = '📖';
      let tagBg = 'rgba(56, 142, 60, 0.08)';
      let tagColor = '#2E7D32';

      if (unit.source_type === 'video') {
        icon = '🎥';
        tagBg = 'rgba(25, 118, 210, 0.08)';
        tagColor = '#1565C0';
      } else if (unit.source_type === 'slide') {
        icon = '🖼️';
        tagBg = 'rgba(245, 124, 0, 0.08)';
        tagColor = '#E65100';
      }

      card.innerHTML = `
        <div>
          <!-- Top Row: Source Type & Topic -->
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; flex-wrap: wrap; gap: 0.35rem;">
            <span style="background: ${tagBg}; border: 1px solid ${tagColor}33; color: ${tagColor}; font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: var(--radius-sm); letter-spacing: 0.05em;">
              ${icon} ${unit.source_type.toUpperCase()}
            </span>
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); font-weight: 500;">
              ${unit.topic_name}
            </span>
          </div>

          <!-- Unit Title -->
          <h4 style="font-family: var(--font-serif); font-size: 1.12rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.35rem; line-height: 1.4;">
            ${unit.title}
          </h4>

          <!-- Exact Grounding Citation -->
          <div style="font-family: var(--font-mono); font-size: 0.76rem; font-weight: 600; color: var(--accent); margin-bottom: 0.65rem;">
            📌 ${unit.citation_label}
          </div>

          <!-- Text Excerpt -->
          <p style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 0.75rem; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
            "${unit.text_content}"
          </p>

          <!-- Badges for Diagram and Equations -->
          <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.75rem;">
            ${unit.visual_description ? `
              <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #7B1FA2; background: rgba(123, 31, 162, 0.06); border: 1px solid rgba(123, 31, 162, 0.2); padding: 0.3rem 0.6rem; border-radius: var(--radius-sm); display: flex; align-items: center; gap: 0.35rem;">
                <span>🎨</span> <span>High-Res Vector Diagram Extracted</span>
              </div>
            ` : ''}

            ${unit.equations && unit.equations.length ? `
              <div style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--accent); background: var(--bg-secondary); border: 1px solid var(--border); padding: 0.3rem 0.6rem; border-radius: var(--radius-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ∑ ${unit.equations[0]}
              </div>
            ` : ''}
          </div>

          <!-- Concept Tags -->
          ${unit.concept_tags && unit.concept_tags.length ? `
            <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.5rem;">
              ${unit.concept_tags.slice(0, 3).map(tag => `
                <span style="font-family: var(--font-mono); font-size: 0.7rem; background: var(--bg-secondary); color: var(--text-muted); border: 1px solid var(--border); padding: 0.15rem 0.45rem; border-radius: var(--radius-sm);">
                  #${tag}
                </span>
              `).join('')}
            </div>
          ` : ''}
        </div>

        <!-- Footer Actions -->
        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid var(--border); gap: 0.45rem; flex-wrap: wrap;">
          <button class="btn-outline" style="font-size: 0.75rem; padding: 0.35rem 0.75rem;" onclick="window.openCitationModal('${unit.id}')">
            📌 Inspect Excerpt
          </button>
          <div style="display: flex; gap: 0.35rem;">
            ${unit.visual_description ? `
              <button class="action-pill-btn" style="font-size: 0.72rem; padding: 0.3rem 0.65rem;" onclick="window.openDiagramExplainer('${unit.id}')" title="Analyze diagram elements and tensor flows with AI">
                🔍 Diagram
              </button>
            ` : ''}
            <button class="action-pill-btn" style="font-size: 0.72rem; padding: 0.3rem 0.65rem;" onclick="window.askTutorAboutUnit('${unit.title.replace(/'/g, "\\'")}', '${unit.topic_name.replace(/'/g, "\\'")}')" title="Ask AI Tutor about this unit">
              💬 Tutor
            </button>
          </div>
        </div>
      `;

      container.appendChild(card);
    });
  },

  resetFilters() {
    this.searchQuery = '';
    this.activeFilter = 'all';
    this.activeTopic = 'all';

    const searchInput = document.getElementById('knowledgeSearchInput');
    if (searchInput) searchInput.value = '';

    const topicSelect = document.getElementById('knowledgeTopicFilter');
    if (topicSelect) topicSelect.value = 'all';

    const filterBtns = document.querySelectorAll('.source-filter-btn');
    filterBtns.forEach(btn => {
      btn.classList.toggle('active-toggle', btn.getAttribute('data-filter') === 'all');
    });

    this.renderUnits();
  },

  setupUploadDropzone() {
    const fileInput = document.getElementById('materialFileInput');
    const uploadBtn = document.getElementById('triggerUploadBtn');
    const dropzone = document.getElementById('uploadDropzone');

    if (uploadBtn && fileInput) {
      uploadBtn.addEventListener('click', () => fileInput.click());
      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
          this.uploadFile(e.target.files[0]);
        }
      });
    }

    if (dropzone) {
      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--accent)';
        dropzone.style.background = 'var(--bg-secondary)';
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = 'var(--border)';
        dropzone.style.background = 'var(--bg-card)';
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--border)';
        dropzone.style.background = 'var(--bg-card)';
        if (e.dataTransfer.files.length) {
          this.uploadFile(e.dataTransfer.files[0]);
        }
      });
    }
  },

  async uploadFile(file) {
    const statusEl = document.getElementById('uploadStatusText');
    if (statusEl) statusEl.innerHTML = `<span style="color: var(--accent); font-weight: 500;">⏳ Ingesting ${file.name}... extracting pages, slides & diagrams...</span>`;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Upload failed');
      }
      const data = await res.json();

      if (statusEl) {
        statusEl.innerHTML = `
          <span style="color: #2E7D32; font-weight: 600;">
            ✓ Successfully ingested ${data.filename}! Extracted ${data.units_extracted} content units with exact citations.
          </span>
        `;
      }

      await this.loadCourseUnits();
      if (window.KnowledgeMapModule) window.KnowledgeMapModule.render();
      alert(`Successfully ingested ${file.name}! Knowledge base updated with ${data.units_extracted} new units.`);
    } catch (err) {
      if (statusEl) statusEl.innerHTML = `<span style="color: #B71C1C;">Upload error: ${err.message}</span>`;
    }
  }
};

window.loadDummyMaterials = async function() {
  const statusEl = document.getElementById('uploadStatusText');
  const btn = document.getElementById('loadDummyDataBtn');
  if (btn) btn.disabled = true;
  if (statusEl) statusEl.innerHTML = '<span style="color: var(--accent); font-weight: 500;">⏳ Ingesting sample WebVTT, SRT, and textbook datasets...</span>';

  try {
    const res = await fetch('/api/ingestion/load-dummy-data', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to load sample dummy datasets');
    const data = await res.json();
    if (statusEl) {
      statusEl.innerHTML = `
        <span style="color: #2E7D32; font-weight: 600;">
          ✓ Ingested ${data.new_units_added} content units from ${data.loaded_files.length} sample datasets! Total course units: ${data.total_course_units}.
        </span>
      `;
    }
    // Refresh Knowledge units
    if (window.IngestionModule) await window.IngestionModule.loadCourseUnits();
    // Refresh Knowledge graph
    if (window.KnowledgeMapModule) window.KnowledgeMapModule.render();
    alert(`Successfully ingested sample datasets (${data.loaded_files.join(', ')})! Total units: ${data.total_course_units}`);
  } catch (err) {
    if (statusEl) statusEl.innerHTML = `<span style="color: #B71C1C;">Error: ${err.message}</span>`;
  } finally {
    if (btn) btn.disabled = false;
  }
};

window.askTutorAboutUnit = function(unitTitle, topicName) {
  switchTab('chat');
  const chatInput = document.getElementById('chatInput');
  if (chatInput) {
    chatInput.value = `Explain the key concepts and formulas from "${unitTitle}" in ${topicName}, citing verified course sources.`;
    if (window.ChatModule) window.ChatModule.handleSend();
  }
};
