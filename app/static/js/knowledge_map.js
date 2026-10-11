/**
 * Knowledge Map Module: Interactive Course Flow & Prerequisite DAG Visualization
 */

window.KnowledgeMapModule = {
  canvas: null,
  ctx: null,
  graphData: null,
  selectedNode: null,
  hoveredNode: null,

  async init() {
    this.canvas = document.getElementById('knowledgeGraphCanvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());

    this.setupInteractions();
    await this.render();
  },

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
    if (this.graphData) this.draw();
  },

  async render() {
    try {
      const res = await fetch('/api/knowledge-graph');
      if (!res.ok) return;
      this.graphData = await res.json();
      this.draw();
    } catch (err) {
      console.error('Failed to load knowledge graph:', err);
    }
  },

  draw() {
    if (!this.ctx || !this.graphData) return;
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Warm architectural grid pattern
    ctx.strokeStyle = '#EFECE6';
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
    // Scale node positions to fit canvas
    const xPositions = this.graphData.nodes.map(n => n.x);
    const yPositions = this.graphData.nodes.map(n => n.y);
    const minX = Math.min(...xPositions);
    const maxX = Math.max(...xPositions);
    const minY = Math.min(...yPositions);
    const maxY = Math.max(...yPositions);

    const padX = 140;
    const padY = 90;

    this.graphData.nodes.forEach(node => {
      const scaledX = padX + ((node.x - minX) / (maxX - minX || 1)) * (width - 2 * padX);
      const scaledY = padY + ((node.y - minY) / (maxY - minY || 1)) * (height - 2 * padY);
      nodeMap[node.id] = { ...node, screenX: scaledX, screenY: scaledY };
    });

    // 1. Draw Prerequisite Edges (Curved Bézier Arrows with warm rule styling)
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

      // Arrowhead in Burnished Gold
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

    // 2. Draw Nodes (Editorial Archival Stamp Aesthetic)
    Object.values(nodeMap).forEach(node => {
      const isHovered = this.hoveredNode && this.hoveredNode.id === node.id;
      const isSelected = this.selectedNode && this.selectedNode.id === node.id;
      const radius = isSelected ? 32 : (isHovered ? 29 : 25);

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
        ctx.arc(node.screenX, node.screenY, radius + 7, 0, Math.PI * 2);
        ctx.fillStyle = haloColor;
        ctx.fill();
        ctx.restore();
      }

      // Node Body Circle (Ivory White Card)
      ctx.save();
      ctx.beginPath();
      ctx.arc(node.screenX, node.screenY, radius, 0, Math.PI * 2);
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();

      // Border stroke
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = isSelected ? 3.5 : 2;
      ctx.stroke();

      // Inner Topic Identifier in Playfair Display
      ctx.fillStyle = '#1A1A1A';
      ctx.font = '700 13px "Playfair Display", Georgia, serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`T${node.order}`, node.screenX, node.screenY - 3);

      // Mastery Percentage in IBM Plex Mono
      ctx.font = '600 10px "IBM Plex Mono", monospace';
      ctx.fillStyle = strokeColor;
      ctx.fillText(`${Math.round(node.mastery * 100)}%`, node.screenX, node.screenY + 11);

      // Label below node in Source Sans 3
      ctx.font = '600 12px "Source Sans 3", -apple-system, sans-serif';
      ctx.fillStyle = '#1A1A1A';
      ctx.fillText(node.label, node.screenX, node.screenY + radius + 16);

      ctx.restore();
    });

    this.scaledNodeMap = nodeMap;
  },

  setupInteractions() {
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

    this.canvas.addEventListener('click', (e) => {
      if (this.hoveredNode) {
        this.selectedNode = this.hoveredNode;
        this.showTopicDetails(this.hoveredNode);
        this.draw();
      }
    });
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
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
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

        <div style="display: flex; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--border);">
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
