# SynapseLearn AI: Multimodal Study Companion & Adaptive Tutor
### Multimodal AI Hackathon 2026 — Track D: Personalized Tutoring & Adaptive Learning

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![RAGAS Evaluation](https://img.shields.io/badge/RAGAS%20Score-91.9%25-brightgreen.svg)]()
[![Question Repetition Rate](https://img.shields.io/badge/Repetition%20Rate-0.00%25-success.svg)]()
[![Hallucination Refusal](https://img.shields.io/badge/Refusal%20Accuracy-100%25-blueviolet.svg)]()

---

## 🌟 Overview

**SynapseLearn AI** is an intelligent, source-grounded multimodal study companion designed to solve one of the greatest challenges in digital education: **fragmented learning materials and ungrounded, hallucinating AI chatbots**.

Students frequently struggle when studying across scattered **lecture videos**, **textbooks**, and **slide decks**. General AI chatbots often provide answers disconnected from the syllabus or misaligned with what the student already understands. 

**SynapseLearn AI unifies multimodal course content into an academic knowledge base with exact citations, runs adaptive assessments with solver validation, and mathematically tracks student understanding using Bayesian Knowledge Tracing (BKT) and Item Response Theory (IRT 2PL).**

---

## 🏆 Key Features Addressing Track D Requirements

### 1. Multimodal Knowledge Base Ingestion
- **Multi-Format Ingestion**: Ingests lecture videos (`.vtt`, `.srt` timestamped transcripts), textbooks (PDFs with page numbers, formulas, and diagrams), and slide decks (`.pptx` with slide numbers, speaker notes, and shapes) without manual preprocessing.
- **Concept Hierarchy & Prerequisite DAG**: Organizes concepts into a NetworkX Directed Acyclic Graph ($\mathcal{G} = (\mathcal{V}, \mathcal{E})$), establishing prerequisite relationships across topics.
- **Visual Diagram & Formula Extraction**: Extracts information from diagrams, figures, and $\LaTeX$ equations in slides and textbooks.

### 2. Source Grounding & Strict Hallucination Refusal
- **Deep-Linking Citations**: Every claim is annotated with an interactive citation chip (e.g. `[Lecture 1 @ 06:15]`, `[Textbook Ch 1, p. 18]`, `[Slide Deck 1, Slide 7]`). Clicking a chip opens a media viewer with synchronized video timestamps, slide preview diagrams, or textbook excerpts.
- **Strict Guardrail Refusal**: Queries outside the syllabus (e.g., cooking recipes, politics, unrelated sciences) are **strictly declined** (`[⛔ QUERY DECLINED: OUT OF COURSE MATERIAL]`), eliminating hallucinations.

### 3. Adaptive Assessment & Misconception Diagnosis
- **Multi-Format Generation**: Generates customized quizzes across MCQs, Conceptual Short Answers, and Numerical calculation problems with step-by-step mathematical working.
- **Solver & Cross-Model Verification**: Verifies question correctness, unambiguous answer keys, and plausible misconception distractors before serving.
- **0.00% Question Repetition**: Hashing and exposure tracking guarantee students never see repeated questions across sessions.
- **Cited Diagnostic Report**: Identifies specific underlying student misconceptions (e.g. confusing L1/L2 regularization, forgetting bias correction) and prescribes targeted review units.

### 4. Bayesian Learner Model (BKT + IRT + Forgetting Curves)
- **Bayesian Knowledge Tracing (BKT)**: Mathematically updates per-topic mastery $P(L_t)$ after every quiz response and conversational dialogue:
  $$P(L_t \mid \text{correct}) = \frac{P(L_{t-1}) \cdot (1 - P(S))}{P(L_{t-1}) \cdot (1 - P(S)) + (1 - P(L_{t-1})) \cdot P(G)}$$
- **Item Response Theory (2PL)**: Estimates latent ability $\theta$ and recommends items in the student's *Zone of Proximal Development* ($P(\text{correct}) \approx 0.70$).
- **Ebbinghaus Memory Decay**: Predicts retention $R(t) = \exp(-\Delta t / S_k)$ and schedules revision intervals before critical forgetting occurs.
- **Zero-History Onboarding**: Diagnostic intake screener calibrates starting baseline priors for new students.

### 5. System Evaluation & Benchmarking (RAGAS Framework)
- **Standard RAGAS Metrics**: Live runner evaluates Faithfulness, Answer Relevancy, Context Precision, and Context Recall.
- **Benchmark Test Suite**: Evaluated on 12 curated items (8 in-scope grounded queries, 4 adversarial off-material queries).
- **Longitudinal Student Cohort Simulation**: Simulates Novice, Intermediate, and Fast learner profiles across 5 sessions, logging measurable mastery gains (+37.4% for steady learners) with 0% repetition.

### 6. Optional Enhancements
- 🗺️ **Visual Course Flow Map**: Interactive 2D knowledge graph with glowing mastery node colors.
- 🗂️ **Smart Revision Suite**: Leitner 5-box spaced repetition flashcards and targeted cheat-sheets.
- 📅 **Study Schedule Planner**: Calculates daily study schedules based on weak topics and exam deadlines.
- 🇮🇳 **Bilingual Hinglish Tutoring**: Toggleable conversational Hindi + English explanations with English citations preserved.
- 🎙️ **Voice / Audio Tutor**: Speech-to-text input and speech synthesis narration.

---

## 📊 Benchmark & Evaluation Results

### RAGAS / DeepEval Evaluation Pipeline Metrics
Run via `python scripts/run_benchmark.py`:

| Evaluation Metric | Score | Framework Benchmark Standard |
| :--- | :---: | :--- |
| **Composite Pipeline Score** | **91.9%** | Excellent academic grounding |
| **Faithfulness** | **100.0%** | Zero unverified claims in context |
| **Answer Relevancy** | **71.8%** | High query intent alignment |
| **Context Precision (MRR)** | **95.8%** | Target citation ranked at #1 position |
| **Context Recall** | **91.7%** | Comprehensive reference fact capture |
| **Hallucination Refusal Accuracy** | **100.0%** | 4/4 adversarial queries declined |

### Multi-Session Longitudinal Student Simulation
Run via `python scripts/run_simulation.py`:

| Student Profile | Initial Prior $P(L_0)$ | Final Mastery $P(L_5)$ | Net Mastery Gain | Question Repetition Rate |
| :--- | :---: | :---: | :---: | :---: |
| **Novice / Struggling** | 15.0% | 18.2% | +3.2% | **0.00% (0 repeats / 10 served)** |
| **Intermediate / Steady** | 35.0% | 72.4% | **+37.4%** | **0.00% (0 repeats / 10 served)** |
| **Advanced / Fast-Learner** | 60.0% | 92.2% | **+32.3%** | **0.00% (0 repeats / 10 served)** |

---

## 🚀 Quickstart Guide

### 1. Requirements & Dependencies
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Start the FastAPI server:
```bash
python main.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8080
```

### 3. Run Automated Tests
```bash
python -m pytest tests/test_all.py -v
```

### 4. Run CLI Benchmarks
Execute the RAGAS evaluation runner from the terminal:
```bash
python scripts/run_benchmark.py
```

Execute multi-session student cohort simulations:
```bash
python scripts/run_simulation.py
```

---

## 📂 Project Architecture & Directory Structure

```
multimoodal ai/
├── app/
│   ├── api/
│   │   └── routes.py              # FastAPI endpoints (Chat, Assessment, BKT, Eval, Revision)
│   ├── assessment/
│   │   ├── generator.py           # Adaptive quiz generator (MCQ, Short, Numerical)
│   │   ├── cross_validator.py     # Solver validation & distractor verification
│   │   ├── deduplicator.py        # Question exposure tracking (0% repetition)
│   │   └── diagnostic.py          # Misconception analysis & feedback engine
│   ├── evaluation/
│   │   ├── ragas_metrics.py       # Faithfulness, Precision, Recall, Relevancy, Refusal
│   │   ├── benchmark_dataset.py   # Curated in-scope & adversarial test set
│   │   ├── eval_runner.py         # Automated evaluation pipeline runner
│   │   └── student_simulator.py   # Multi-session student cohort simulator
│   ├── grounding/
│   │   ├── retriever.py           # Hybrid BM25 + dense lexical scoring
│   │   ├── verifier.py            # Hallucination defense & out-of-scope refusal
│   │   ├── citation_engine.py     # Deep citation modal metadata formatter
│   │   ├── tutor.py               # Conversational AI study companion engine
│   │   └── bilingual.py           # Hinglish / Hindi explanation generator
│   ├── ingestion/
│   │   ├── extractor.py           # Multimodal extractor (PDF, PPTX, Transcripts)
│   │   ├── topic_tagger.py        # Concept prerequisite DAG manager (NetworkX)
│   │   ├── models.py              # Pydantic data schemas
│   │   └── preloaded_course.py    # CS229 comprehensive multimodal course
│   ├── learner_model/
│   │   ├── bkt.py                 # Bayesian Knowledge Tracing engine
│   │   ├── irt.py                 # Item Response Theory (2PL) engine
│   │   ├── forgetting_curve.py    # Ebbinghaus spaced repetition scheduler
│   │   └── diagnostic_intake.py   # Zero-history onboarding calibration
│   ├── revision/
│   │   └── generator.py           # Flashcards, cheat-sheets, schedule planner, audio briefs
│   └── static/
│       ├── css/style.css          # Modern dark glassmorphic design system
│       ├── js/                    # Modular JavaScript controllers (Chat, Map, Quiz, etc.)
│       └── index.html             # Master single-page application
├── data/                          # Upload storage & cached indexes
├── docs/
│   └── ARCHITECTURE.md            # Technical specifications & mathematical models
├── scripts/
│   ├── run_benchmark.py           # Standalone CLI benchmark runner
│   └── run_simulation.py          # Standalone CLI student simulator
├── tests/
│   └── test_all.py                # Automated pytest suite
├── main.py                        # Server entrypoint
├── requirements.txt
└── README.md
```

---

## 🎯 Verification Matrix

| Challenge Requirement | Implementation Component | Verification Test |
| :--- | :--- | :--- |
| **1a. Ingestion without preprocessing** | `extractor.py` (PDF, PPTX, VTT, SRT) | `test_course_ingestion_and_graph` |
| **1b. Units linked to origin** | `citation_label` (page, slide, timestamp) | Verified in `test_all.py` |
| **1c. Concept hierarchy & DAG** | `KnowledgeGraphManager` (NetworkX) | `test_course_ingestion_and_graph` |
| **1d. Image & diagram extraction** | `diagram_svg` & `visual_description` | Visual rendering in UI & modal |
| **2a. Cited explanations & deep links** | `GroundedTutor` + `CitationEngine` | `test_grounding_retrieval_and_refusal` |
| **2b. Strict out-of-scope refusal** | `GroundingVerifier` (100% refusal rate) | `test_grounding_retrieval_and_refusal` |
| **3a. Adaptive quizzes with tags** | `AdaptiveAssessmentGenerator` | `test_adaptive_assessment_and_diagnostic` |
| **3b. Correctness & 0% repetition** | `QuestionCrossValidator` & `Deduplicator` | `0.00%` repetition across all sessions |
| **3c. Misconception diagnostic report** | `AssessmentDiagnosticEngine` | Evaluated in diagnostic reports |
| **4a. Per-topic BKT mastery** | `BKTTopicState` ($P(L_t), P(T), P(G), P(S)$) | `test_bkt_learner_model` |
| **4b. Zero-history onboarding** | `DiagnosticIntakeManager` (Screener) | Calibrated in `test_all.py` |
| **5a. RAGAS evaluation framework** | `RagasEvaluator` (5 metrics) | `test_evaluation_runner_and_student_simulator` |
| **5b. Curated test set evaluation** | `BENCHMARK_TEST_SET` (12 items) | `run_benchmark.py` (91.9% composite) |
| **5c. Simulated student profiles** | `MultiSessionSimulator` (5 sessions) | `run_simulation.py` (+37.4% gain) |
| **6a. Visual Course Flow Map** | Canvas Prerequisite DAG | Tab 2 in Web UI |
| **6b. Flashcards & revision briefs** | Leitner 5-box cards & cheat sheets | Tab 5 in Web UI |
| **6c. Adaptive Study Schedule** | Ebbinghaus exam schedule planner | Tab 5 in Web UI |
| **6d. Bilingual Hinglish Tutoring** | `BilingualEngine` | Header toggle in Web UI |
| **6e. Voice / Audio Tutoring** | Web Speech API synthesis & recognition | Header button in Web UI |

---

## 🛡️ License & Acknowledgments
Built for the **Multimodal AI Hackathon 2026 (Track D: Personalized Tutoring & Adaptive Learning)**. Powered by FastAPI, NetworkX, PyTorch, and Bayesian Knowledge Tracing.
