# SkillRack Agent

Automate SkillRack Python programming problem solving.

## Status

- **Python3-H013 Files** (2904-2912) ✅
- **Python3-H014 Classes & Objects** (2912-2921) ✅
- **Python3-H015 Miscellaneous** (2922-2928) ✅
- **50 EASY CHALLENGES** (PART001-PART005) ✅

## Setup

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Launch Chrome with remote debugging
google-chrome --remote-debugging-port=9222

# Log in to SkillRack in the opened browser
```

## How to Use

### Find unsolved problems
```bash
python skillrack.py --list -m codetutor
python skillrack.py --list -m codetrack
```

### Read a problem
```bash
python skillrack.py <PID> -r -m codetutor
```

### Solve a problem
Write your solution to a .py file, then:
```bash
python skillrack.py <PID> solution.py -m codetutor -l PYTHON3
```

The tool handles navigation, CAPTCHA solving, code pasting, running, and result detection.

### If a problem fails
Read the error output, fix your code, and re-run. The CAPTCHA re-appears each submission.

## Project Files

| File | Purpose |
|------|---------|
| `solutions.py` | PID → solution mapping (all completed PIDs) |
| `captcha.py` | CAPTCHA solver (PIL + tesseract OCR) |
| `nav.py` | Browser navigation helpers |
| `run.py` | Code paste + Run + result detection |
| `qread.py` | Read problem descriptions |
| `solver.py` | Main solve loop |
| `course_solver.py` | Course-specific fill-in-blank solver |
| `skillrack.py` | CLI entry point |
| `editor.py` | Ace editor interaction |
| `status.py` | Completion status checker |
| `prompt.txt` | Detailed agent instructions |

## Key Details

- **Run button**: `j_id_a3` (course) / `j_id_bg` (Easy challenges)
- **CAPTCHA**: simple addition, OCR with `--psm 6 --oem 3` (no whitelist)
- **Fill-in-blanks**: server template uses `____` placeholders
- **Navigation**: `trackshome.xhtml` → Level 1 → CODETUTOR → Python → EASY → Part → PID
