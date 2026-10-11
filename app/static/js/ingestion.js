/**
 * Ingestion & Multimodal Knowledge Hub Module:
 * File drag-and-drop ingestion (PDF, PPTX, Transcripts) and course source unit browser.
 */

window.IngestionModule = {
  currentUnits: [],
  activeFilter: 'all',

  async init() {
    await this.loadCourseUnits();
    this.setupUploadDropzone();
    this.setupFilterTabs();
  },

  async loadCourseUnits() {
    try {
      const res = await fetch('/api/course');
      if (!res.ok) return;
      const data = await res.json();
      this.currentUnits = data.content_units || [];
      this.renderUnits();
    } catch (err) {
      console.error('Failed to load course units:', err);
    }
  },

  setupFilterTabs() {
    const filterBtns = document.querySelectorAll('.source-filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active-toggle'));
        btn.classList.add('active-toggle');
        this.activeFilter = btn.getAttribute('data-filter');
        this.renderUnits();
      });
    });
  },

  renderUnits() {
    const container = document.getElementById('knowledgeUnitsGrid');
    if (!container) return;
    container.innerHTML = '';

    const filtered = this.activeFilter === 'all'
      ? this.currentUnits
      : this.currentUnits.filter(u => u.source_type === this.activeFilter);

    filtered.forEach(unit => {
      const card = document.createElement('div');
      card.className = 'glass-card';
      card.style.display = 'flex';
      card.style.flexDirection = 'column';
      card.style.justifyContent = 'space-between';
      card.style.borderTop = '3px solid var(--accent)';

      let icon = '📖';
      if (unit.source_type === 'video') {
        icon = '🎥';
      } else if (unit.source_type === 'slide') {
        icon = '🖼️';
      }

      card.innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.65rem;">
            <span style="background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text-main); font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: var(--radius-sm); letter-spacing: 0.05em;">
              ${icon} ${unit.source_type.toUpperCase()}
            </span>
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">${unit.topic_name}</span>
          </div>

          <h4 style="font-family: var(--font-serif); font-size: 1.15rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.35rem; line-height: 1.4;">
            ${unit.title}
          </h4>

          <div style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600; color: var(--accent); margin-bottom: 0.75rem;">
            📌 ${unit.citation_label}
          </div>

          <p style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 0.85rem;">
            ${unit.text_content.substring(0, 140)}...
          </p>

          ${unit.visual_description ? `
            <div style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--accent); background: var(--accent-muted); border: 1px solid var(--border); padding: 0.35rem 0.65rem; border-radius: var(--radius-sm); margin-bottom: 0.85rem;">
              🎨 Diagram Extracted
            </div>
          ` : ''}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.85rem; border-top: 1px solid var(--border);">
          <span style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-muted);">
            ${unit.concept_tags ? unit.concept_tags.slice(0, 2).join(', ') : ''}
          </span>
          <button class="btn-outline" style="font-size: 0.75rem; padding: 0.3rem 0.75rem;" onclick="window.openCitationModal('${unit.id}')">
            Inspect Unit
          </button>
        </div>
      `;

      container.appendChild(card);
    });
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
        dropzone.style.borderColor = 'var(--primary)';
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = 'var(--border-subtle)';
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--border-subtle)';
        if (e.dataTransfer.files.length) {
          this.uploadFile(e.dataTransfer.files[0]);
        }
      });
    }
  },

  async uploadFile(file) {
    const statusEl = document.getElementById('uploadStatusText');
    if (statusEl) statusEl.innerText = `Ingesting ${file.name}... parsing pages, slides & diagrams...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error('Upload failed');
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
      alert(`Successfully ingested ${file.name}! Knowledge base updated.`);
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

