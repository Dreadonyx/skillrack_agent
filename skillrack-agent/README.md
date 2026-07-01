# SkillRack Agent

Automated problem-solving for SkillRack programming courses using Playwright + Brave/Chrome remote debugging.

## Status

### Python3 Course ✅
| Chapter | Status |
|---------|--------|
| H013 Files | ✅ |
| H014 Classes & Objects | ✅ |
| H015 Miscellaneous | ✅ |
| 50 EASY CHALLENGES Parts 1-5 | ✅ |

### Data Structures in C Course ✅
| Chapter | Units | Status |
|---------|-------|--------|
| H001 Array Implementation of List | 6 | ✅ |
| H002 Linked List (SLL, DLL, CDLL) | 9 | ✅ |
| H003 Array Implementation of Stack | 5 | ✅ |
| H004 Array Implementation of Queue | 3 | ✅ |
| H005 Linked List Implementation of Stack | 1 | ✅ |
| H006 Linked List Implementation of Queue | 1 | ✅ |
| H007 Binary Search Tree | 6 | ✅ |
| H008 Heap | 3 | ✅ |
| H009 Graph (DFS, BFS, Reachable) | 3 | ✅ |
| H010 Hash Table | 1 | ✅ |

## Setup

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Launch Chrome/Brave with remote debugging
google-chrome --remote-debugging-port=9222
# or
brave-browser --remote-debugging-port=9222

# Log in to SkillRack in the opened browser
```

## Usage

### List unsolved problems
```bash
python skillrack.py --list -m codetutor
python skillrack.py --list -m codetrack
```

### Read a problem
```bash
python skillrack.py <PID> -r -m codetutor
```

### Solve a problem
```bash
python skillrack.py <PID> solution.py -m codetutor -l PYTHON3
python skillrack.py <PID> solution.c -m codetutor -l C
```

## Project Files

| File | Purpose |
|------|---------|
| `skillrack.py` | CLI entry point |
| `solutions.py` | PID → solution mapping |
| `solver.py` | Main solve loop |
| `course_solver.py` | Course fill-in-blank solver |
| `run.py` | Code paste + Run + result detection |
| `nav.py` | Browser navigation helpers |
| `captcha.py` | CAPTCHA solver (PIL + Tesseract OCR) |
| `editor.py` | Ace editor interaction |
| `qread.py` | Read problem descriptions |
| `status.py` | Page status checker |
| `list_unsolved.py` | Unsolved problem lister |
| `prompt.txt` | Detailed agent instructions |

## Key Details

- **Run button**: `j_id_a3` (course) / `j_id_bg` (Easy challenges)
- **CAPTCHA**: simple addition, OCR with `--psm 6 --oem 3`
- **Fill-in-blanks**: server template uses `____` placeholders; only paste missing code
- **C course**: Problems use Ace editor with global `struct Node` pointers; 1-indexed positions
