/**
 * Knowledge Map Module: Interactive Course Flow & Prerequisite DAG Visualization
 */

window.KnowledgeMapModule = {
  canvas: null,
  ctx: null,
  graphData: null,
  selectedNode: null,
  hoveredNode: null,
  scaledNodeMap: {},
  isInitialized: false,

  async init() {
    this.canvas = document.getElementById('knowledgeGraphCanvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    if (!this.isInitialized) {
      this.setupInteractions();
      window.addEventListener('resize', () => {
        if (AppState.activeTab === 'map') {
          this.resizeCanvas();
        }
      });
      this.isInitialized = true;
    }

    await this.render();
  },

  async onTabActivated() {
    this.canvas = document.getElementById('knowledgeGraphCanvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    if (!this.isInitialized) {
      this.setupInteractions();
      window.addEventListener('resize', () => {
        if (AppState.activeTab === 'map') {
          this.resizeCanvas();
        }
      });
      this.isInitialized = true;
    }

    // Two-step RAF ensures DOM layout has calculated non-zero dimensions
    requestAnimationFrame(() => {
      requestAnimationFrame(async () => {
        this.resizeCanvas();
        if (!this.graphData) {
          await this.render();
        } else {
          this.draw();
        }

        // Auto-select topic-1 if nothing selected yet
        if (!this.selectedNode && this.graphData && this.graphData.nodes && this.graphData.nodes.length) {
          const first = this.graphData.nodes[0];
          this.selectedNode = first;
          this.showTopicDetails(first);
          const jumpSelect = document.getElementById('mapTopicJumpSelect');
          if (jumpSelect) jumpSelect.value = first.id;
          this.draw();
        }
      });
    });
  },

  resizeCanvas() {
    if (!this.canvas) return;
    const parent = this.canvas.parentElement;
    if (!parent) return;

    const rect = parent.getBoundingClientRect();
    const w = Math.floor(rect.width || parent.clientWidth || 900);
    const h = Math.floor(rect.height || parent.clientHeight || 520);

    if (w <= 0 || h <= 0) return;

    this.canvas.width = w;
    this.canvas.height = h;

    if (this.graphData) {
      this.draw();
    }
  },

  async render() {
    try {
      const res = await fetch('/api/knowledge-graph');
      if (!res.ok) return;
      this.graphData = await res.json();
      this.resizeCanvas();
      this.draw();

      if (!this.selectedNode && this.graphData.nodes && this.graphData.nodes.length) {
        const first = this.graphData.nodes[0];
        this.selectedNode = first;
        this.showTopicDetails(first);
        const jumpSelect = document.getElementById('mapTopicJumpSelect');
        if (jumpSelect) jumpSelect.value = first.id;
      }
    } catch (err) {
      console.error('Failed to load knowledge graph:', err);
    }
  },

  draw() {
    if (!this.ctx || !this.graphData || !this.canvas) return;
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;

    if (width <= 0 || height <= 0) return;

    ctx.clearRect(0, 0, width, height);

    // 1. Subtle warm architectural grid pattern
    ctx.strokeStyle = '#F0ECE4';
    ctx.lineWidth = 1;
    const step = 40;
    for (let x = 0; x < width; x += step) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += step) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    const nodeMap = {};
    const xPositions = this.graphData.nodes.map(n => n.x);
    const yPositions = this.graphData.nodes.map(n => n.y);
    const minX = Math.min(...xPositions);
    const maxX = Math.max(...xPositions);
    const minY = Math.min(...yPositions);
    const maxY = Math.max(...yPositions);

    const isSmallScreen = width < 680;
    const padX = isSmallScreen ? 50 : Math.max(90, Math.min(140, width * 0.12));
    const padY = isSmallScreen ? 55 : Math.max(65, Math.min(95, height * 0.16));

    const drawW = Math.max(100, width - 2 * padX);
    const drawH = Math.max(100, height - 2 * padY);

    this.graphData.nodes.forEach(node => {
      const scaledX = padX + ((node.x - minX) / (maxX - minX || 1)) * drawW;
      const scaledY = padY + ((node.y - minY) / (maxY - minY || 1)) * drawH;
      nodeMap[node.id] = { ...node, screenX: scaledX, screenY: scaledY };
    });
    this.scaledNodeMap = nodeMap;

    // 2. Draw Prerequisite Edges (Curved Bézier Arrows)
    this.graphData.edges.forEach(edge => {
      const source = nodeMap[edge.from];
      const target = nodeMap[edge.to];
      if (!source || !target) return;

      ctx.beginPath();
      ctx.strokeStyle = '#D1CCC4';
      ctx.lineWidth = 2;

      const midX = (source.screenX + target.screenX) / 2;
      ctx.moveTo(source.screenX, source.screenY);
      ctx.bezierCurveTo(midX, source.screenY, midX, target.screenY, target.screenX, target.screenY);
      ctx.stroke();

      // Golden Arrowhead
      const angle = Math.atan2(target.screenY - source.screenY, target.screenX - midX);
      ctx.save();
      ctx.translate(target.screenX - 28 * Math.cos(angle), target.screenY - 28 * Math.sin(angle));
      ctx.rotate(angle);
      ctx.beginPath();
      ctx.moveTo(-9, -4.5);
      ctx.lineTo(0, 0);
      ctx.lineTo(-9, 4.5);
      ctx.fillStyle = '#B8860B';
      ctx.fill();
      ctx.restore();
    });

    // 3. Draw Nodes (Ivory Card Aesthetic)
    Object.values(nodeMap).forEach(node => {
      const isHovered = this.hoveredNode && this.hoveredNode.id === node.id;
      const isSelected = this.selectedNode && this.selectedNode.id === node.id;
      const radius = isSelected ? 30 : (isHovered ? 28 : 24);

      let strokeColor = '#8C8883'; // Learning
      let haloColor = 'rgba(140, 136, 131, 0.12)';
      if (node.mastery >= 0.85) {
        strokeColor = '#2E7D32'; // Mastered
        haloColor = 'rgba(46, 125, 50, 0.15)';
      } else if (node.mastery >= 0.50) {
        strokeColor = '#B8860B'; // Developing
        haloColor = 'rgba(184, 134, 11, 0.16)';
      }

      // Outer Halo for Hover/Selection
      if (isHovered || isSelected) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(node.screenX, node.screenY, radius + 8, 0, Math.PI * 2);
        ctx.fillStyle = haloColor;
        ctx.fill();
        ctx.restore();
      }

      // Node Body Circle
      ctx.save();
      ctx.beginPath();
      ctx.arc(node.screenX, node.screenY, radius, 0, Math.PI * 2);
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();

      // Border stroke
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = isSelected ? 3.5 : 2;
      ctx.stroke();

      // Topic Identifier
      ctx.fillStyle = '#1A1A1A';
      ctx.font = '700 12px "Playfair Display", Georgia, serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`T${node.order}`, node.screenX, node.screenY - 3);

      // Mastery Percentage
      ctx.font = '600 10px "IBM Plex Mono", monospace';
      ctx.fillStyle = strokeColor;
      ctx.fillText(`${Math.round(node.mastery * 100)}%`, node.screenX, node.screenY + 10);

      // Label below node
      ctx.font = '600 11px "Source Sans 3", -apple-system, sans-serif';
      ctx.fillStyle = '#1A1A1A';
      let displayLabel = node.label;
      if (isSmallScreen && displayLabel.length > 18) {
        displayLabel = displayLabel.substring(0, 16) + '...';
      }
      ctx.fillText(displayLabel, node.screenX, node.screenY + radius + 15);

      ctx.restore();
    });
  },

  setupInteractions() {
    if (!this.canvas) return;

    // Mouse Move
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      let found = null;
      if (this.scaledNodeMap) {
        Object.values(this.scaledNodeMap).forEach(node => {
          const dist = Math.hypot(node.screenX - mouseX, node.screenY - mouseY);
          if (dist <= 35) found = node;
        });
      }

      if (found !== this.hoveredNode) {
        this.hoveredNode = found;
        this.canvas.style.cursor = found ? 'pointer' : 'default';
        this.draw();
      }
    });

    // Mouse Click
    this.canvas.addEventListener('click', (e) => {
      if (this.hoveredNode) {
        this.selectNode(this.hoveredNode);
      }
    });

    // Touch Support for Mobile / Tablet
    this.canvas.addEventListener('touchstart', (e) => {
      if (!e.touches.length) return;
      const rect = this.canvas.getBoundingClientRect();
      const touch = e.touches[0];
      const mouseX = touch.clientX - rect.left;
      const mouseY = touch.clientY - rect.top;

      let found = null;
      if (this.scaledNodeMap) {
        Object.values(this.scaledNodeMap).forEach(node => {
          const dist = Math.hypot(node.screenX - mouseX, node.screenY - mouseY);
          if (dist <= 40) found = node;
        });
      }

      if (found) {
        e.preventDefault();
        this.selectNode(found);
      }
    }, { passive: false });
  },

  selectNode(node) {
    this.selectedNode = node;
    this.hoveredNode = node;
    this.showTopicDetails(node);
    const jumpSelect = document.getElementById('mapTopicJumpSelect');
    if (jumpSelect) jumpSelect.value = node.id;
    this.draw();
  },

  showTopicDetails(node) {
    const detailsContainer = document.getElementById('mapTopicDetails');
    if (!detailsContainer) return;

    let badgeBg = 'rgba(140, 136, 131, 0.1)';
    let badgeColor = '#8C8883';
    let statusLabel = 'Learning';
    if (node.mastery >= 0.85) {
      badgeBg = 'rgba(46, 125, 50, 0.1)';
      badgeColor = '#2E7D32';
      statusLabel = 'Mastered';
    } else if (node.mastery >= 0.50) {
      badgeBg = 'rgba(184, 134, 11, 0.1)';
      badgeColor = '#B8860B';
      statusLabel = 'Developing';
    }

    detailsContainer.innerHTML = `
      <div style="background: var(--bg-card); border: 1px solid var(--border); border-top: 3px solid var(--accent); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <span style="font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.12em; color: var(--accent);">
              TOPIC #${node.order}
            </span>
            <h3 style="font-family: var(--font-serif); font-size: 1.25rem; font-weight: 700; color: var(--text-main); margin-top: 0.25rem;">
              ${node.label}
            </h3>
          </div>
          <span style="background: ${badgeBg}; color: ${badgeColor}; font-family: var(--font-mono); font-weight: 600; font-size: 0.78rem; padding: 0.3rem 0.75rem; border-radius: var(--radius-sm); letter-spacing: 0.05em;">
            ${Math.round(node.mastery * 100)}% (${statusLabel})
          </span>
        </div>

        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.7; margin-bottom: 1.25rem;">
          ${node.description}
        </p>

        <div style="margin-bottom: 1.25rem; padding-top: 0.85rem; border-top: 1px solid var(--border);">
          <div style="font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">
            Core Concepts & Prerequisite Foundations:
          </div>
          <div style="display: flex; flex-wrap: wrap; gap: 0.45rem;">
            ${node.key_concepts.map(c => `
              <span style="background: var(--bg-secondary); border: 1px solid var(--border); padding: 0.25rem 0.65rem; border-radius: var(--radius-sm); font-size: 0.82rem; color: var(--text-main);">
                ${c}
              </span>
            `).join('')}
          </div>
        </div>

        <div style="display: flex; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--border); flex-wrap: wrap;">
          <button class="btn-primary" style="font-size: 0.85rem; padding: 0.55rem 1.1rem;" onclick="window.startTopicQuiz('${node.id}')">
            📝 Take Quiz on Topic
          </button>
          <button class="btn-outline" style="font-size: 0.85rem; padding: 0.55rem 1.1rem;" onclick="window.askTutorAboutTopic('${node.label}')">
            💬 Ask Tutor
          </button>
        </div>
      </div>
    `;
  }
};

window.selectTopicFromDropdown = function(topicId) {
  if (!topicId || !window.KnowledgeMapModule.scaledNodeMap) return;
  const node = window.KnowledgeMapModule.scaledNodeMap[topicId];
  if (node) {
    window.KnowledgeMapModule.selectNode(node);
  }
};

window.startTopicQuiz = function(topicId) {
  switchTab('assessment');
  if (window.AssessmentModule) {
    window.AssessmentModule.generateQuizForTopic(topicId);
  }
};

window.askTutorAboutTopic = function(topicName) {
  switchTab('chat');
  const chatInput = document.getElementById('chatInput');
  if (chatInput) {
    chatInput.value = `Explain the core concepts and mathematical formulations of ${topicName} citing course materials.`;
    if (window.ChatModule) window.ChatModule.handleSend();
  }
};
