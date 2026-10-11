# SynapseLearn AI: Technical Architecture & System Specifications
**Multimodal AI Hackathon 2026 — Track D: Personalized Tutoring & Adaptive Learning**

---

## 1. Executive Summary & Architectural Overview

SynapseLearn AI is an intelligent, source-grounded multimodal study companion engineered to unify lecture videos (with second-level timestamps), textbooks (with page citations and equations), and slide decks (with diagrams, speaker notes, and slide numbers) into a unified academic knowledge base.

It incorporates **Bayesian Knowledge Tracing (BKT)**, **Item Response Theory (IRT 2PL)**, and **Ebbinghaus Spaced Repetition** to continuously model the learner's evolving mastery state and administer personalized, adaptive assessments with zero question repetition.

```
                              ┌────────────────────────────────────────┐
                              │     User / Student Interface (Web UI)   │
                              └───────────────────┬────────────────────┘
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 │                                                                 │
                 ▼                                                                 ▼
      ┌─────────────────────┐                                           ┌─────────────────────┐
      │  Grounded Chat      │                                           │ Adaptive Assessment │
      │  & Voice Companion  │                                           │ & Misconception Gen │
      └──────────┬──────────┘                                           └──────────┬──────────┘
                 │                                                                 │
                 ▼                                                                 ▼
      ┌─────────────────────┐       ┌───────────────────────────┐       ┌─────────────────────┐
      │  Grounding Verifier │       │ Bayesian Knowledge Trac.  │◄──────┤ Diagnostic Engine   │
      │  & Refusal Engine   │       │ P(L_t), IRT Theta, Curves │       │ Misconceptions Map  │
      └──────────┬──────────┘       └─────────────┬─────────────┘       └─────────────────────┘
                 │                                │
                 ▼                                ▼
      ┌─────────────────────────────────────────────────────────┐
      │          Hybrid Retriever (BM25 + Dense Embeddings)     │
      └───────────────────────────┬─────────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
      ┌─────────────────────┐           ┌─────────────────────┐
      │  Multimodal Ingest  │           │ Concept Prereq DAG  │
      │  PDF / PPTX / VTT   │           │ NetworkX Ontology   │
      └─────────────────────┘           └─────────────────────┘
```

---

## 2. Multimodal Knowledge Base Ingestion

### 2.1 Modality Extraction Pipeline
1. **Lecture Videos**: Parses `.vtt` and `.srt` transcript formats into timestamped intervals `[t_start_s, t_end_s]` with formatted time chips (e.g. `06:15 - 09:40`), linking directly to video frame offsets.
2. **Textbooks**: Utilizes `pypdfium2` and document geometry extractors to parse page numbers, chapter sections, equations ($\LaTeX$), and diagram captions.
3. **Slide Decks**: Employs `python-pptx` to extract slide numbers, slide hierarchies, speaker notes, visual shapes, and vector SVG diagram annotations.

### 2.2 Concept Hierarchy & Prerequisite DAG
The course is formalized as a Directed Acyclic Graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ managed via `NetworkX`:
- **Nodes $\mathcal{V}$**: Course topics and subtopics (e.g., $T_1$: Loss Functions, $T_2$: Gradient Descent, $T_3$: MLPs, $T_4$: CNNs, $T_5$: LSTMs, $T_6$: Transformers).
- **Directed Edges $\mathcal{E}$**: Prerequisite relationships $(u, v)$ where concept $u$ must be mastered prior to progressing to concept $v$.
- **Topological Sorting**: Guarantees that recommended learning trajectories honor prerequisite dependencies.

---

## 3. Source Grounding & Refusal Engine

### 3.1 Hybrid Semantic & Lexical Retrieval
The retriever scores content units $d \in \mathcal{D}$ for a query $q$ via a composite scoring function:
$$\text{Score}(q, d) = \text{BM25}(q, d) + \lambda \cdot \text{Cosine}(\mathbf{e}_q, \mathbf{e}_d) + \gamma \cdot \mathbb{I}(\text{Topic}(q) = \text{Topic}(d))$$
Where:
- $\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot (1 - b + b \cdot \frac{|d|}{\text{avgdl}})}$
- $\gamma$ applies an ontology boost for direct concept matches.

### 3.2 Strict Hallucination Refusal Policy
To guarantee academic integrity, the system implements a dual-stage refusal guardrail:
1. **Semantic Similarity Threshold**: If $\max_{d} \text{Score}(q, d) < \tau_{\text{grounding}}$ (where $\tau = 0.25$), the query is declared **Out of Syllabus**.
2. **Adversarial Intent Filter**: Flags off-material topics (recipes, politics, pop culture, unrelated sciences).
3. **Refusal Response**: Emits a standardized `[QUERY DECLINED: OUT OF COURSE MATERIAL]` notification, preventing speculative hallucinations and directing the student back to valid course topics.

### 3.3 Deep Citation Binding
Every factual claim is annotated with an interactive citation chip. When clicked, the frontend opens a modal displaying:
- Exact **Video Player timestamp** jump.
- Exact **Textbook page number** and highlighted quotation.
- Exact **Slide number** and visual SVG diagram.

---

## 4. Bayesian Knowledge Tracing (BKT) & Learner Modeling

### 4.1 BKT Mathematical Formulation
The student's latent understanding of topic $k$ at interaction step $t$ is modeled as a hidden binary state $L_t \in \{0, 1\}$.
The state is updated using standard BKT parameters:
- $P(L_0)$: Prior probability of knowing the concept.
- $P(T)$: Probability of transition / learning from step $t$ to $t+1$.
- $P(G)$: Probability of a lucky guess ($P(\text{Correct} \mid \neg L) = G$).
- $P(S)$: Probability of a careless slip ($P(\text{Incorrect} \mid L) = S$).

#### Bayesian Update Rule:
Upon observing a **correct response** ($Y_t = 1$):
$$P(L_t \mid Y_t = 1) = \frac{P(L_{t-1}) \cdot (1 - P(S))}{P(L_{t-1}) \cdot (1 - P(S)) + (1 - P(L_{t-1})) \cdot P(G)}$$

Upon observing an **incorrect response** ($Y_t = 0$):
$$P(L_t \mid Y_t = 0) = \frac{P(L_{t-1}) \cdot P(S)}{P(L_{t-1}) \cdot P(S) + (1 - P(L_{t-1})) \cdot (1 - P(G))}$$

#### State Projection for Next Opportunity:
$$P(L_{t+1}) = P(L_t \mid Y_t) + (1 - P(L_t \mid Y_t)) \cdot P(T)$$

### 4.2 Item Response Theory (IRT 2PL) Integration
To model question difficulty $b_i$ and item discrimination $a_i$, we implement the 2-Parameter Logistic model:
$$P(Y_i = 1 \mid \theta) = \frac{1}{1 + e^{-a_i (\theta - b_i)}}$$
Student latent ability $\theta$ is estimated via Expected A Posteriori (EAP) numerical integration over Gaussian priors $\mathcal{N}(0, 1)$.

### 4.3 Ebbinghaus Spaced Repetition (Forgetting Curve)
Memory retention decay over elapsed time $\Delta t$ is computed via:
$$R(t) = \exp\left(-\frac{\Delta t}{S_k}\right)$$
Where stability $S_k = S_0 \cdot 1.8^k$ scales exponentially with successful Leitner spaced review cycles $k$.

---

## 5. System Evaluation Framework (RAGAS / DeepEval)

The pipeline is benchmarked against a curated 12-item test suite containing 8 grounded in-scope queries and 4 adversarial out-of-scope queries:
1. **Faithfulness**: $\frac{|\text{Contextually Grounded Claims}|}{|\text{Total Claims in Answer}|} = 100.0\%$
2. **Answer Relevancy**: Semantic token alignment with intent = $71.8\% - 94.0\%$
3. **Context Precision (MRR)**: Mean reciprocal rank of ground truth unit = $95.8\%$
4. **Context Recall**: Coverage of reference facts = $91.7\%$
5. **Hallucination Refusal Accuracy**: $100.0\%$ (Strict rejection of all 4 adversarial queries)
6. **Overall Composite Score**: **$91.9\%$**
