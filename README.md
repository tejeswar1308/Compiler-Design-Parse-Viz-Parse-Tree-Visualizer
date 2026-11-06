# ParseViz — Interactive Parse Tree Generator

> A full-stack educational web application for exploring context-free grammars, LL(1) parsing, and parse-tree visualization. Built for the Compiler Design Hackathon.

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Grammar Editor** | Enter CFGs with multi-character symbols, epsilon support, and real-time validation |
| **Left Recursion Elimination** | Immediate and indirect left recursion removal with step-by-step explanation |
| **Left Factoring** | Automatic prefix factoring with conflict-free symbol naming |
| **FIRST & FOLLOW Sets** | Fixed-point iteration algorithms with epsilon propagation |
| **LL(1) Parsing Table** | Full predictive parsing table with conflict detection |
| **Parsing Simulator** | Step-by-step trace with play/pause/step controls |
| **Parse Tree Visualization** | Interactive tree with zoom, pan, and node details |
| **Practice Mode** | Auto-generated questions validated by real algorithms |

---

## 🏗️ Architecture

```
ParseViz/
├── backend/              # Python FastAPI server
│   ├── app/
│   │   ├── main.py       # FastAPI app entry point
│   │   ├── models/       # Pydantic request/response models
│   │   ├── services/     # Compiler algorithm implementations
│   │   └── api/          # API route handlers
│   ├── tests/            # Pytest test suite
│   └── requirements.txt
│
├── frontend/             # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript types
│   │   └── utils/        # Tree layout utilities
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## 🛠️ Technology Stack

### Backend
- **Python 3.10+** — core language
- **FastAPI** — REST API framework
- **Pydantic v2** — request/response validation
- **Uvicorn** — ASGI server
- **Pytest** — test framework

### Frontend
- **React 18** with **TypeScript**
- **Vite** — build tooling
- **Tailwind CSS** — utility-first styling
- **ReactFlow** — parse tree visualization
- **Framer Motion** — animations
- **Lucide React** — icons
- **Axios** — HTTP client

---

## 📋 Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| pip | latest | `pip --version` |

---

## ⚡ Installation & Setup

### 1. Clone / Open the Project

Open the `Hackathon Project` folder in VS Code.

### 2. Backend Setup (Terminal 1 — PowerShell)

```powershell
# Navigate to backend
cd "d:\KL\SEM - 5\CD\Hackathon Project\backend"

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at: `http://localhost:8000`
API docs (Swagger UI): `http://localhost:8000/docs`

### 3. Frontend Setup (Terminal 2 — PowerShell)

```powershell
# Navigate to frontend
cd "d:\KL\SEM - 5\CD\Hackathon Project\frontend"

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/examples` | Get 5 sample grammars |
| `POST` | `/api/grammar/validate` | Parse and validate a CFG |
| `POST` | `/api/grammar/transform/left-recursion` | Eliminate left recursion |
| `POST` | `/api/grammar/transform/left-factoring` | Apply left factoring |
| `POST` | `/api/grammar/first-follow` | Compute FIRST and FOLLOW sets |
| `POST` | `/api/grammar/parsing-table` | Build LL(1) parsing table |
| `POST` | `/api/grammar/parse` | Simulate predictive parsing |
| `POST` | `/api/practice/generate` | Generate a practice question |
| `POST` | `/api/practice/check` | Check a practice answer |

### Request Format

All `POST` endpoints accept JSON:
```json
{ "grammar_text": "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id", "start_symbol": "E" }
```

---

## 📚 Sample Grammars

### 1. Arithmetic (Left Recursive)
```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

### 2. Needs Left Factoring
```
S -> i E t S e S | i E t S | a
E -> b
```

### 3. Simple LL(1)
```
S -> a B C
B -> b B | ε
C -> c | ε
```

### 4. Epsilon Productions
```
A -> B C D
B -> b | ε
C -> c | ε
D -> d | ε
```

### 5. LL(1) Conflict Grammar
```
S -> A a | A b
A -> a | ε
```

---

## 🧪 Running Tests

```powershell
# Navigate to backend
cd "d:\KL\SEM - 5\CD\Hackathon Project\backend"

# Activate venv if not already activated
.\.venv\Scripts\Activate.ps1

# Run all 97 tests across algorithms and API
pytest tests/ -v
```

---

## 🎯 Hackathon Demo Walkthrough

### Scenario 1: Arithmetic Grammar Full Flow

1. **Open** `http://localhost:5173`
2. **Select** the "Arithmetic (Left Recursive)" sample from the dropdown
3. **Grammar Workspace**: Click "Validate Grammar" — see nonterminals, terminals, start symbol
4. **Left Recursion**: Click "Eliminate Left Recursion" — shows E and T have recursion, step-by-step elimination
5. Click "Use Transformed Grammar" to proceed with the LL(1)-ready grammar
6. **Left Factoring**: Click "Apply Left Factoring" — verify no factoring needed after LR elimination
7. **FIRST & FOLLOW**: Click "Compute" — see complete FIRST/FOLLOW tables
8. **LL(1) Table**: Click "Build Table" — shows full predictive parsing table, no conflicts
9. **Parsing Simulator**: Enter `id + id * id`, click "Parse"
10. Watch step-by-step trace, then click "Play" to animate
11. **Parse Tree**: View the interactive tree; click nodes for details

### Scenario 2: Conflict Grammar

1. Select "LL(1) Conflict Grammar" from dropdown
2. Skip to LL(1) Table — see red conflict cells highlighted
3. See explanation of which transformations may resolve conflicts

### Scenario 3: Practice Mode

1. Navigate to Practice Mode
2. Select "FIRST Set" question type
3. Generate and answer questions
4. Review step-by-step explanations

---

## 🔧 Troubleshooting

| Error | Solution |
|---|---|
| `venv\Scripts\Activate.ps1 cannot be loaded` | Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `ModuleNotFoundError: No module named 'fastapi'` | Ensure venv is activated, run `pip install -r requirements.txt` |
| `CORS error in browser` | Ensure backend is running on port 8000 |
| `npm: command not found` | Install Node.js from https://nodejs.org |
| Frontend shows blank / API errors | Check backend is running, check browser console |
| `Port 8000 already in use` | Run `uvicorn app.main:app --reload --port 8001` and update vite.config.ts proxy |

---

## 📁 Folder Structure (Detailed)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry, CORS config
│   ├── models/
│   │   ├── __init__.py
│   │   └── grammar.py             # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── grammar_parser.py      # CFG parsing & validation
│   │   ├── tokenizer.py           # Input string tokenization
│   │   ├── left_recursion.py      # Left recursion elimination
│   │   ├── left_factoring.py      # Left factoring algorithm
│   │   ├── first_follow.py        # FIRST/FOLLOW computation
│   │   ├── parsing_table.py       # LL(1) table construction
│   │   ├── predictive_parser.py   # Parsing simulation
│   │   ├── parse_tree.py          # Parse tree generation
│   │   └── practice_generator.py  # Practice question generation
│   └── api/
│       ├── __init__.py
│       └── routes.py              # All API endpoints
└── tests/
    ├── __init__.py
    └── test_algorithms.py         # Comprehensive test suite

frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── GrammarEditor.tsx
│   │   ├── TransformationPanel.tsx
│   │   ├── FirstFollowPanel.tsx
│   │   ├── ParsingTable.tsx
│   │   ├── ParsingSimulator.tsx
│   │   ├── ParseTreeView.tsx
│   │   ├── PracticePanel.tsx
│   │   └── ErrorPanel.tsx
│   ├── hooks/
│   │   └── useGrammar.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   └── treeLayout.ts
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── tsconfig.json
```

---

## 🎨 Design System

- **Background**: `#0a0f1e` (deepest), `#111827`, `#1f2937`
- **Sidebar**: `#0f172a`
- **Cards**: `#111827` with `border #1f2937`
- **Primary**: Blue `#3b82f6`
- **Secondary**: Cyan `#06b6d4`
- **Tertiary**: Violet `#8b5cf6`
- **Success**: Green `#22c55e`
- **Error**: Red `#ef4444`
- **Warning**: Amber `#f59e0b`
- **Font**: System UI / monospace for code

---

## 👨‍💻 Development Notes

- Backend algorithms use no external AI — pure Python implementations
- All algorithms terminate via fixed-point iteration with cycle detection
- Grammar parser uses whitespace tokenization (not character-by-character)
- ε (epsilon) is normalized consistently throughout the codebase
- Parse tree is derived from actual production sequence during parsing
- Practice questions are generated using real grammar instances
