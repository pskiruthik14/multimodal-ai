"""
Preloaded Comprehensive Course: CS229: Deep Learning & Neural Architectures
Includes Multimodal lecture video transcripts with timestamps,
textbook chapters with exact page numbers, and slide decks with slide numbers and extracted diagrams.
"""

from typing import List
from app.ingestion.models import Course, Topic, ContentUnit, SourceType

COURSE_TOPICS: List[Topic] = [
    Topic(
        id="topic-1",
        name="Loss Functions & Optimization Landscapes",
        description="Mathematical formulation of objective functions, MSE, Cross-Entropy, convexity, and loss surfaces.",
        order=1,
        prerequisites=[],
        key_concepts=["Mean Squared Error", "Cross-Entropy Loss", "Empirical Risk", "Convexity", "Hessian Matrix"]
    ),
    Topic(
        id="topic-2",
        name="Gradient Descent & Adaptive Optimizers",
        description="First-order optimization methods: Batch GD, Mini-batch SGD, Momentum, RMSProp, and Adam.",
        order=2,
        prerequisites=["topic-1"],
        key_concepts=["Gradient Descent", "Stochastic Gradient Descent", "Momentum", "Learning Rate", "Adam Optimizer"]
    ),
    Topic(
        id="topic-3",
        name="Multi-Layer Perceptrons & Backpropagation",
        description="Feedforward neural networks, non-linear activation functions, computational graphs, and the chain rule.",
        order=3,
        prerequisites=["topic-2"],
        key_concepts=["Activation Functions", "ReLU", "Computational Graph", "Chain Rule", "Vanishing Gradients"]
    ),
    Topic(
        id="topic-4",
        name="Convolutional Neural Networks (CNNs)",
        description="Spatial feature extraction, 2D convolution kernels, stride, padding, pooling, and ResNet skip connections.",
        order=4,
        prerequisites=["topic-3"],
        key_concepts=["Convolution Kernel", "Feature Map", "Stride and Padding", "Receptive Field", "Residual Connections"]
    ),
    Topic(
        id="topic-5",
        name="Sequence Modeling & Recurrent Networks",
        description="Temporal dynamics, recurrent connections, BPTT, and gated units (LSTM, GRU).",
        order=5,
        prerequisites=["topic-3"],
        key_concepts=["Hidden State", "Recurrent Neural Network", "BPTT", "LSTM", "Forget Gate"]
    ),
    Topic(
        id="topic-6",
        name="Self-Attention & Transformer Architecture",
        description="Attention mechanisms, Scaled Dot-Product, Multi-Head Attention, and positional encodings.",
        order=6,
        prerequisites=["topic-5"],
        key_concepts=["Scaled Dot-Product Attention", "Query Key Value", "Multi-Head Attention", "Positional Encoding", "LayerNorm"]
    )
]

PRELOADED_UNITS: List[ContentUnit] = [
    # ------------------ TOPIC 1: Loss Functions ------------------
    ContentUnit(
        id="unit-v1-01",
        title="Lecture 1: The Geometry of Loss Functions",
        source_type=SourceType.VIDEO,
        source_name="Lecture 1: Foundations of Optimization",
        citation_label="Lecture 1 @ 06:15",
        timestamp_start_s=375,
        timestamp_end_s=580,
        timestamp_formatted="06:15 - 09:40",
        text_content="In supervised learning, our goal is to minimize empirical risk over training examples. For regression, Mean Squared Error penalizes larger errors quadratically: L_MSE = (1/2N) sum (y_i - f(x_i))^2. For classification, Cross-Entropy Loss measures the divergence between true label distribution and predicted probabilities: L_CE = -sum y_i * log(p_i). Notice how cross-entropy provides steep gradients when predictions are confidently wrong, preventing gradient saturation.",
        equations=["L_{MSE} = \\frac{1}{2N} \\sum_{i=1}^N (y_i - \\hat{y}_i)^2", "L_{CE} = -\\sum_{i=1}^C y_i \\log(\\hat{y}_i)"],
        topic_id="topic-1",
        topic_name="Loss Functions & Optimization Landscapes",
        concept_tags=["Mean Squared Error", "Cross-Entropy Loss", "Empirical Risk"],
        video_embed_url="https://www.youtube-nocookie.com/embed/aircAruvnKk?start=375"
    ),
    ContentUnit(
        id="unit-tb-01",
        title="Textbook Ch 1: Convexity and Ill-Conditioned Curvature",
        source_type=SourceType.TEXTBOOK,
        source_name="Deep Learning: Foundations & Principles",
        citation_label="Textbook Ch 1, p. 18",
        page_number=18,
        text_content="Page 18, Section 1.4: Convexity implies that any local minimum is a global minimum. However, deep neural network loss surfaces are non-convex, characterized by saddle points, ravines, and plateaus. The local curvature is given by the Hessian matrix H = d^2 L / dw^2. If eigenvalues of H have vastly different magnitudes (condition number lambda_max / lambda_min >> 1), the loss landscape is an elongated canyon, causing standard gradient descent to oscillate wildly across steep walls rather than moving along the ravine floor.",
        visual_description="Figure 1.4: 3D contour plot of an ill-conditioned quadratic bowl showing gradient descent bouncing between steep ravines instead of progressing towards the minimum.",
        diagram_svg='<svg viewBox="0 0 400 200" class="diagram-svg"><ellipse cx="200" cy="100" rx="170" ry="40" fill="none" stroke="#6366f1" stroke-width="2"/><ellipse cx="200" cy="100" rx="110" ry="25" fill="none" stroke="#818cf8" stroke-width="2"/><ellipse cx="200" cy="100" rx="40" ry="10" fill="none" stroke="#10b981" stroke-width="3"/><path d="M 50 80 Q 140 140 160 85 T 195 100" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="4"/><text x="185" y="105" fill="#10b981" font-size="12" font-weight="bold">Min*</text><text x="60" y="70" fill="#ef4444" font-size="10">Oscillating SGD Path</text></svg>',
        equations=["H_{i,j} = \\frac{\\partial^2 L}{\\partial w_i \\partial w_j}", "\\kappa = \\frac{\\lambda_{max}}{\\lambda_{min}}"],
        topic_id="topic-1",
        topic_name="Loss Functions & Optimization Landscapes",
        concept_tags=["Convexity", "Hessian Matrix", "Loss Landscapes"]
    ),
    ContentUnit(
        id="unit-sl-01",
        title="Slide 7: Cross-Entropy vs Squared Error for Softmax",
        source_type=SourceType.SLIDE,
        source_name="Lecture Deck 1: Optimization Surfaces",
        citation_label="Slide Deck 1, Slide 7",
        slide_number=7,
        text_content="Why use Cross-Entropy over MSE for classification with Softmax? 1) MSE gradient with sigmoid/softmax contains factor sigma'(z) = sigma(z)(1 - sigma(z)), which saturates toward 0 when prediction is very wrong. 2) Cross-entropy directly cancels this saturation term: dL/dz = (p - y), yielding linear gradient response proportional to prediction error. Key takeaway: Never pair MSE with Softmax output in classification.",
        equations=["\\frac{\\partial L_{CE}}{\\partial z_k} = \\hat{y}_k - y_k"],
        topic_id="topic-1",
        topic_name="Loss Functions & Optimization Landscapes",
        concept_tags=["Cross-Entropy Loss", "Activation Functions"]
    ),

    # ------------------ TOPIC 2: Gradient Descent & Optimizers ------------------
    ContentUnit(
        id="unit-v1-02",
        title="Lecture 1: Momentum and Adaptive Learning Rates",
        source_type=SourceType.VIDEO,
        source_name="Lecture 1: Foundations of Optimization",
        citation_label="Lecture 1 @ 21:40",
        timestamp_start_s=1300,
        timestamp_end_s=1580,
        timestamp_formatted="21:40 - 26:20",
        text_content="Standard SGD updates weights as w_{t+1} = w_t - alpha * grad_t. But in ravines, SGD oscillates. Polyak's Momentum adds velocity vector: v_t = beta * v_{t-1} + (1 - beta) * grad_t, acting like a heavy ball rolling downhill. High-frequency oscillations cancel out, while consistent directions accelerate. In practice, beta=0.9 is standard.",
        equations=["v_t = \\beta v_{t-1} + (1-\\beta) \\nabla_w L(w_t)", "w_{t+1} = w_t - \\alpha v_t"],
        topic_id="topic-2",
        topic_name="Gradient Descent & Adaptive Optimizers",
        concept_tags=["Momentum", "Stochastic Gradient Descent", "Gradient Descent"],
        video_embed_url="https://www.youtube-nocookie.com/embed/aircAruvnKk?start=1300"
    ),
    ContentUnit(
        id="unit-tb-02",
        title="Textbook Ch 2: Adam: Adaptive Moment Estimation",
        source_type=SourceType.TEXTBOOK,
        source_name="Deep Learning: Foundations & Principles",
        citation_label="Textbook Ch 2, p. 45",
        page_number=45,
        text_content="Page 45, Section 2.3: The Adam optimizer combines both first-moment (momentum) and second-moment (RMSProp) running estimates of gradients. m_t = beta_1 * m_{t-1} + (1 - beta_1) * g_t, and v_t = beta_2 * v_{t-1} + (1 - beta_2) * g_t^2. Crucially, Adam applies bias correction: m_hat = m_t / (1 - beta_1^t) and v_hat = v_t / (1 - beta_2^t) to counteract zero-initialization bias in early iterations. The parameter update is w_{t+1} = w_t - alpha * m_hat / (sqrt(v_hat) + eps).",
        visual_description="Figure 2.3: Comparison chart of SGD, Momentum, RMSProp, and Adam trajectories on the Beale test function.",
        diagram_svg='<svg viewBox="0 0 400 200" class="diagram-svg"><path d="M 40 160 Q 150 150 200 110 T 350 40" fill="none" stroke="#10b981" stroke-width="3"/><path d="M 40 160 Q 80 180 120 120 T 260 90 T 350 40" fill="none" stroke="#f59e0b" stroke-width="2"/><path d="M 40 160 L 60 175 L 80 145 L 110 170 L 150 130" fill="none" stroke="#ef4444" stroke-width="1.5"/><circle cx="350" cy="40" r="5" fill="#10b981"/><text x="260" y="35" fill="#10b981" font-size="11" font-weight="bold">Adam (Fastest)</text><text x="180" y="75" fill="#f59e0b" font-size="11">Momentum</text><text x="70" y="190" fill="#ef4444" font-size="10">SGD (Oscillating)</text></svg>',
        equations=[
            "\\hat{m}_t = \\frac{m_t}{1 - \\beta_1^t}",
            "\\hat{v}_t = \\frac{v_t}{1 - \\beta_2^t}",
            "\\theta_{t+1} = \\theta_t - \\frac{\\alpha}{\\sqrt{\\hat{v}_t} + \\epsilon} \\hat{m}_t"
        ],
        topic_id="topic-2",
        topic_name="Gradient Descent & Adaptive Optimizers",
        concept_tags=["Adam Optimizer", "Learning Rate", "Momentum"]
    ),
    ContentUnit(
        id="unit-sl-02",
        title="Slide 14: Learning Rate Schedules and Warmup",
        source_type=SourceType.SLIDE,
        source_name="Lecture Deck 1: Optimization Surfaces",
        citation_label="Slide Deck 1, Slide 14",
        slide_number=14,
        text_content="Why is learning rate warmup necessary in modern transformers and deep nets? In early steps, variance of gradient estimates is high because moving averages v_t are noisy. A large initial learning rate destabilizes early layers. Linear warmup gradually ramps learning rate from 0 to alpha_max over the first W warmup steps, followed by Cosine Annealing decay to zero.",
        equations=["\\alpha(t) = \\frac{t}{W} \\alpha_{max} \\quad (t \\le W)", "\\alpha(t) = \\alpha_{min} + \\frac{1}{2}(\\alpha_{max}-\\alpha_{min})(1 + \\cos(\\frac{t-W}{T-W}\\pi))"],
        topic_id="topic-2",
        topic_name="Gradient Descent & Adaptive Optimizers",
        concept_tags=["Learning Rate", "Adam Optimizer"]
    ),

    # ------------------ TOPIC 3: MLPs & Backpropagation ------------------
    ContentUnit(
        id="unit-v2-01",
        title="Lecture 2: Computational Graphs and the Chain Rule",
        source_type=SourceType.VIDEO,
        source_name="Lecture 2: Multi-Layer Perceptrons & Backprop",
        citation_label="Lecture 2 @ 14:30",
        timestamp_start_s=870,
        timestamp_end_s=1180,
        timestamp_formatted="14:30 - 19:40",
        text_content="Backpropagation is simply recursive application of the chain rule over a directed acyclic computational graph. During forward pass, we compute intermediate node outputs and cache them. During backward pass, each node receives upstream gradient dL/dz and multiplies it by local Jacobian dz/dx to pass downstream gradients dL/dx. Gradients sum at branching nodes where an output influences multiple downstream nodes: dL/dx = sum_j (dL/dy_j * dy_j/dx).",
        equations=["\\frac{\\partial L}{\\partial x} = \\sum_{j \\in children(x)} \\frac{\\partial L}{\\partial y_j} \\frac{\\partial y_j}{\\partial x}"],
        topic_id="topic-3",
        topic_name="Multi-Layer Perceptrons & Backpropagation",
        concept_tags=["Computational Graph", "Chain Rule"],
        video_embed_url="https://www.youtube-nocookie.com/embed/aircAruvnKk?start=870"
    ),
    ContentUnit(
        id="unit-tb-03",
        title="Textbook Ch 3: Vanishing Gradients and Non-linearities",
        source_type=SourceType.TEXTBOOK,
        source_name="Deep Learning: Foundations & Principles",
        citation_label="Textbook Ch 3, p. 68",
        page_number=68,
        text_content="Page 68, Section 3.2: Why did Sigmoid and Tanh hinder deep network training? For Sigmoid sigma(z) = 1/(1+e^-z), the derivative sigma'(z) = sigma(z)(1-sigma(z)) has maximum value of 0.25 at z=0 and asymptotes to 0 as |z| grows. In a 10-layer network, the product of 10 terms <= 0.25 scales down gradient by at least (1/4)^10 ~ 10^-6! This vanishing gradient problem rendered early layers untrained. Rectified Linear Unit ReLU(z) = max(0, z) has derivative exactly 1 for z > 0, completely avoiding saturation along active pathways.",
        visual_description="Figure 3.2: Graph comparing derivatives of Sigmoid (peak 0.25), Tanh (peak 1.0 but fast decay), and ReLU (constant 1 for positive z).",
        diagram_svg='<svg viewBox="0 0 400 200" class="diagram-svg"><line x1="30" y1="170" x2="370" y2="170" stroke="#64748b" stroke-width="1"/><line x1="200" y1="20" x2="200" y2="180" stroke="#64748b" stroke-width="1"/><path d="M 40 170 L 200 170 L 360 40" fill="none" stroke="#10b981" stroke-width="3"/><path d="M 40 168 Q 160 165 200 135 T 360 168" fill="none" stroke="#3b82f6" stroke-width="2"/><text x="320" y="35" fill="#10b981" font-size="12" font-weight="bold">ReLU (f\'=1)</text><text x="210" y="125" fill="#3b82f6" font-size="11">Sigmoid (max 0.25)</text></svg>',
        equations=["\\sigma\'(z) = \\sigma(z)(1 - \\sigma(z)) \\le 0.25", "\\frac{\\partial}{\\partial z} \\text{ReLU}(z) = \\begin{cases} 1 & z > 0 \\\\ 0 & z < 0 \\end{cases}"],
        topic_id="topic-3",
        topic_name="Multi-Layer Perceptrons & Backpropagation",
        concept_tags=["Vanishing Gradients", "Activation Functions", "ReLU"]
    ),
    ContentUnit(
        id="unit-sl-03",
        title="Slide 11: Dying ReLU and Leaky ReLU Solutions",
        source_type=SourceType.SLIDE,
        source_name="Lecture Deck 2: Backprop & Architectures",
        citation_label="Slide Deck 2, Slide 11",
        slide_number=11,
        text_content="Dying ReLU Problem: If a neuron's activation falls into the negative regime (z < 0) for all data samples, its gradient is 0, so weight updates cease permanently. The neuron is dead. Remedies: 1) Leaky ReLU: f(z) = max(alpha*z, z) with alpha=0.01. 2) Parametric ReLU (PReLU) where alpha is learned. 3) GELU (Gaussian Error Linear Unit) used in GPT and BERT, smoothing the threshold with x * Phi(x).",
        equations=["\\text{LeakyReLU}(z) = \\max(0.01z, z)", "\\text{GELU}(x) \\approx 0.5x(1 + \\tanh(\\sqrt{2/\\pi}(x + 0.044715x^3)))"],
        topic_id="topic-3",
        topic_name="Multi-Layer Perceptrons & Backpropagation",
        concept_tags=["ReLU", "Activation Functions"]
    ),

    # ------------------ TOPIC 4: Convolutional Neural Networks ------------------
    ContentUnit(
        id="unit-v3-01",
        title="Lecture 3: Convolution Kernels, Strides, and Padding",
        source_type=SourceType.VIDEO,
        source_name="Lecture 3: Convolutional Neural Networks",
        citation_label="Lecture 3 @ 09:20",
        timestamp_start_s=560,
        timestamp_end_s=890,
        timestamp_formatted="09:20 - 14:50",
        text_content="Convolution layers exploit spatial locality and translation invariance by sliding parameter-shared kernels over the input image. Given input dimensions W x H, kernel size K, padding P, and stride S, the output spatial dimension is O = floor((W - K + 2P)/S) + 1. For example, a 32x32 image with 3x3 kernel, padding 1, and stride 1 preserves dimensions at (32 - 3 + 2)/1 + 1 = 32x32. Zero-padding prevents spatial resolution from collapsing too quickly in deep networks.",
        equations=["O = \\left\\lfloor \\frac{W - K + 2P}{S} \\right\\rfloor + 1"],
        topic_id="topic-4",
        topic_name="Convolutional Neural Networks (CNNs)",
        concept_tags=["Convolution Kernel", "Stride and Padding", "Feature Map"],
        video_embed_url="https://www.youtube-nocookie.com/embed/aircAruvnKk?start=560"
    ),
    ContentUnit(
        id="unit-tb-04",
        title="Textbook Ch 4: Residual Learning and ResNet Skip Connections",
        source_type=SourceType.TEXTBOOK,
        source_name="Deep Learning: Foundations & Principles",
        citation_label="Textbook Ch 4, p. 102",
        page_number=102,
        text_content="Page 102, Section 4.5: As networks grew deeper (e.g. 20 vs 56 layers), researchers observed degradation: higher training error, not caused by overfitting. He et al. (2015) introduced Residual Learning. Instead of hoping stacked layers fit underlying mapping H(x), we explicitly let layers fit residual F(x) = H(x) - x, recasting output as H(x) = F(x) + x. The shortcut connection x passes identity. During backpropagation, the gradient is dL/dx = dL/dH * (dF/dx + 1). The '+1' term acts as a gradient superhighway, flowing directly back through layers without vanishing even if dF/dx is small.",
        visual_description="Figure 4.5: ResNet Building Block diagram showing input x splitting into weight layers F(x) and an identity shortcut line curving to an addition node (+) to form F(x) + x followed by ReLU.",
        diagram_svg='<svg viewBox="0 0 400 200" class="diagram-svg"><rect x="120" y="40" width="100" height="35" rx="5" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/><text x="135" y="62" fill="#e2e8f0" font-size="11">Weight Layer</text><rect x="120" y="105" width="100" height="35" rx="5" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/><text x="135" y="127" fill="#e2e8f0" font-size="11">Weight Layer</text><circle cx="170" cy="170" r="14" fill="#10b981" stroke="#fff" stroke-width="2"/><text x="165" y="175" fill="#fff" font-size="16" font-weight="bold">+</text><path d="M 170 15 L 170 40" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)"/><path d="M 170 75 L 170 105" stroke="#94a3b8" stroke-width="2"/><path d="M 170 140 L 170 156" stroke="#94a3b8" stroke-width="2"/><path d="M 170 25 C 290 25 290 170 184 170" fill="none" stroke="#f59e0b" stroke-width="3" stroke-dasharray="4"/><text x="300" y="95" fill="#f59e0b" font-size="11" font-weight="bold">Identity Skip: x</text><text x="75" y="175" fill="#10b981" font-size="12" font-weight="bold">F(x) + x</text></svg>',
        equations=["\\mathcal{H}(x) = \\mathcal{F}(x) + x", "\\frac{\\partial L}{\\partial x} = \\frac{\\partial L}{\\partial \\mathcal{H}} \\left( \\frac{\\partial \\mathcal{F}}{\\partial x} + 1 \\right)"],
        topic_id="topic-4",
        topic_name="Convolutional Neural Networks (CNNs)",
        concept_tags=["Residual Connections", "Receptive Field"]
    ),
    ContentUnit(
        id="unit-sl-04",
        title="Slide 18: Receptive Field Growth and Dilated Convolutions",
        source_type=SourceType.SLIDE,
        source_name="Lecture Deck 3: CNN Architectures",
        citation_label="Slide Deck 3, Slide 18",
        slide_number=18,
        text_content="Receptive field is the region in the input space that a particular feature in a layer looks at. Two stacked 3x3 convolutions have receptive field of 5x5, using 2*(3*3)=18 weights compared to a single 5x5 filter with 25 weights (28% fewer parameters + extra non-linearity!). Dilated (atrous) convolutions expand receptive field exponentially without losing spatial resolution by inserting spaces between kernel weights.",
        equations=["RF_{out} = RF_{in} + (K - 1) \\times J_{in}"],
        topic_id="topic-4",
        topic_name="Convolutional Neural Networks (CNNs)",
        concept_tags=["Receptive Field", "Convolution Kernel"]
    ),

    # ------------------ TOPIC 5: Sequence Modeling & RNNs ------------------
    ContentUnit(
        id="unit-v4-01",
        title="Lecture 4: Vanishing Gradients in RNNs and LSTM Cells",
        source_type=SourceType.VIDEO,
        source_name="Lecture 4: Sequences, RNNs and Attention",
        citation_label="Lecture 4 @ 12:10",
        timestamp_start_s=730,
        timestamp_end_s=1040,
        timestamp_formatted="12:10 - 17:20",
        text_content="Vanilla RNN updates hidden state h_t = tanh(W_hh * h_{t-1} + W_xh * x_t). When backpropagating through T time steps, gradient dh_T / dh_1 involves product of T weight matrices (W_hh)^T. If largest singular value of W_hh < 1, gradient vanishes exponentially; if > 1, it explodes. LSTM fixes this with constant error carousel via cell state C_t governed by three gates: Forget gate f_t, Input gate i_t, and Output gate o_t.",
        equations=[
            "f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)",
            "i_t = \\sigma(W_i [h_{t-1}, x_t] + b_i)",
            "\\tilde{C}_t = \\tanh(W_c [h_{t-1}, x_t] + b_c)",
            "C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t",
            "o_t = \\sigma(W_o [h_{t-1}, x_t] + b_o)",
            "h_t = o_t \\odot \\tanh(C_t)"
        ],
        topic_id="topic-5",
        topic_name="Sequence Modeling & Recurrent Networks",
        concept_tags=["LSTM", "Forget Gate", "Hidden State", "BPTT"],
        video_embed_url="https://www.youtube-nocookie.com/embed/aircAruvnKk?start=730"
    ),
    ContentUnit(
        id="unit-tb-05",
        title="Textbook Ch 5: Gated Architectures & The Memory Highway",
        source_type=SourceType.TEXTBOOK,
        source_name="Deep Learning: Foundations & Principles",
        citation_label="Textbook Ch 5, p. 128",
        page_number=128,
        text_content="Page 128, Section 5.3: Notice the cell state update C_t = f_t * C_{t-1} + i_t * C_tilde_t. If forget gate f_t = 1 and input gate i_t = 0, cell state C_t = C_{t-1} exactly. Gradients flow backwards through time along C_t through linear addition without being multiplied by weight matrices. This creates a gradient highway across hundreds of time steps, solving the long-term dependency bottleneck that crippled vanilla RNNs.",
        visual_description="Figure 5.3: LSTM cell diagram displaying horizontal top conveyor belt line for cell state C_t with elementwise multiplication by f_t and addition of candidate update.",
        diagram_svg='<svg viewBox="0 0 400 200" class="diagram-svg"><rect x="50" y="40" width="300" height="130" rx="10" fill="#0f172a" stroke="#6366f1" stroke-width="2"/><line x1="20" y1="70" x2="380" y2="70" stroke="#f59e0b" stroke-width="3"/><circle cx="120" cy="70" r="12" fill="#ef4444"/><text x="115" y="75" fill="#fff" font-size="14">x</text><circle cx="230" cy="70" r="12" fill="#10b981"/><text x="224" y="75" fill="#fff" font-size="14">+</text><text x="320" y="60" fill="#f59e0b" font-size="11" font-weight="bold">Cell State C_t</text><text x="70" y="115" fill="#94a3b8" font-size="11">Forget Gate f_t</text><text x="190" y="115" fill="#94a3b8" font-size="11">Input Gate i_t</text></svg>',
        equations=["\\frac{\\partial C_t}{\\partial C_{t-1}} = f_t"],
        topic_id="topic-5",
        topic_name="Sequence Modeling & Recurrent Networks",
        concept_tags=["LSTM", "Forget Gate", "Recurrent Neural Network"]
    ),

    # ------------------ TOPIC 6: Self-Attention & Transformers ------------------
    ContentUnit(
        id="unit-v4-02",
        title="Lecture 4: Scaled Dot-Product and Multi-Head Attention",
        source_type=SourceType.VIDEO,
        source_name="Lecture 4: Sequences, RNNs and Attention",
        citation_label="Lecture 4 @ 29:15",
        timestamp_start_s=1755,
        timestamp_end_s=2100,
        timestamp_formatted="29:15 - 35:00",
        text_content="Why does Transformer compute Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V? 1) Q K^T computes dot-product compatibility between query vector and all key vectors. 2) Scaling factor 1/sqrt(d_k) is critical: for large head dimensions d_k, dot products grow large in magnitude, pushing softmax into regions with extremely small gradients. Dividing by sqrt(d_k) restores variance to 1. 3) Multi-Head Attention projects Q, K, V into h different subspaces, allowing model to attend to information from different representation positions simultaneously.",
        equations=[
            "\\text{Attention}(Q, K, V) = \\text{softmax}\\left( \\frac{Q K^T}{\\sqrt{d_k}} \\right) V",
            "\\text{MultiHead}(Q, K, V) = \\text{Concat}(\\text{head}_1, \\dots, \\text{head}_h) W^O",
            "\\text{head}_i = \\text{Attention}(Q W_i^Q, K W_i^K, V W_i^V)"
        ],
        topic_id="topic-6",
        topic_name="Self-Attention & Transformer Architecture",
        concept_tags=["Scaled Dot-Product Attention", "Query Key Value", "Multi-Head Attention"],
        video_embed_url="https://www.youtube-nocookie.com/embed/aircAruvnKk?start=1755"
    ),
    ContentUnit(
        id="unit-tb-06",
        title="Textbook Ch 6: Positional Encoding in Transformers",
        source_type=SourceType.TEXTBOOK,
        source_name="Deep Learning: Foundations & Principles",
        citation_label="Textbook Ch 6, p. 154",
        page_number=154,
        text_content="Page 154, Section 6.2: Self-attention is permutation-equivariant: shuffling the input token sequence yields the exact same attention outputs, just permuted. Since order matters in language, we must inject positional information. Vaswani et al. use sinusoidal positional encodings: PE(pos, 2i) = sin(pos / 10000^(2i/d_model)) and PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model)). This allows the model to easily learn relative positions because for any fixed offset k, PE(pos+k) can be represented as a linear function of PE(pos).",
        visual_description="Figure 6.2: Heatmap matrix of sinusoidal positional encodings across 512 embedding dimensions over 100 sequence positions showing varying frequency wave patterns.",
        diagram_svg='<svg viewBox="0 0 400 200" class="diagram-svg"><rect x="30" y="30" width="340" height="140" rx="6" fill="#1e1b4b" stroke="#818cf8" stroke-width="2"/><path d="M 40 60 Q 120 20 200 60 T 360 60" fill="none" stroke="#ec4899" stroke-width="2"/><path d="M 40 100 Q 80 80 120 100 T 200 100 T 280 100 T 360 100" fill="none" stroke="#06b6d4" stroke-width="2"/><path d="M 40 140 Q 60 130 80 140 T 120 140 T 160 140 T 200 140 T 240 140 T 280 140 T 320 140 T 360 140" fill="none" stroke="#10b981" stroke-width="1.5"/><text x="45" y="52" fill="#ec4899" font-size="10">Low Freq (dim 0)</text><text x="45" y="92" fill="#06b6d4" font-size="10">Mid Freq (dim 64)</text><text x="45" y="132" fill="#10b981" font-size="10">High Freq (dim 256)</text></svg>',
        equations=[
            "PE_{(pos, 2i)} = \\sin\\left( \\frac{pos}{10000^{2i/d_{model}}} \\right)",
            "PE_{(pos, 2i+1)} = \\cos\\left( \\frac{pos}{10000^{2i/d_{model}}} \\right)"
        ],
        topic_id="topic-6",
        topic_name="Self-Attention & Transformer Architecture",
        concept_tags=["Positional Encoding", "Query Key Value"]
    ),
    ContentUnit(
        id="unit-sl-06",
        title="Slide 22: O(N^2) Computational Complexity of Attention",
        source_type=SourceType.SLIDE,
        source_name="Lecture Deck 4: Transformers & Scaling",
        citation_label="Slide Deck 4, Slide 22",
        slide_number=22,
        text_content="Self-Attention computes Q K^T where Q, K in R^{N x d}. Matrix multiplication produces an N x N attention matrix. Memory and compute scale quadratically O(N^2 * d) with sequence length N. For sequence length N=512, N^2 = 2.6e5. For N=32,768, N^2 = 1.07e9! This quadratic wall motivates FlashAttention (tiling SRAM cache), Linear Attention, and Sliding Window Attention used in long-context models.",
        equations=["\\text{FLOPs} = 4Nd^2 + 2N^2d", "\\text{Memory Complexity} = \\mathcal{O}(N^2)"],
        topic_id="topic-6",
        topic_name="Self-Attention & Transformer Architecture",
        concept_tags=["Scaled Dot-Product Attention", "Multi-Head Attention"]
    )
]

def get_preloaded_course() -> Course:
    return Course(
        id="cs229-dl",
        name="CS229: Deep Learning & Neural Architectures",
        code="CS229-DL",
        description="Comprehensive graduate course unifying foundational optimization, deep multi-layer perceptrons, CNNs, sequence models, and Transformer architectures.",
        topics=COURSE_TOPICS,
        content_units=PRELOADED_UNITS
    )
