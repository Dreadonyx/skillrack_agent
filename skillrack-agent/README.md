# SkillRack Automation Agent

Automate SkillRack problem solving end-to-end. Handles navigation, CAPTCHA,
language selection, code pasting, running, and result detection — all without
manual interaction.

## Requirements

- Python 3.8+
- Google Chrome / Brave running with `--remote-debugging-port=9222`
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (`apt install tesseract-ocr`)
- Logged-in SkillRack session in the browser

## Quick Start

```bash
pip install -r requirements.txt
playwright install chromium
google-chrome --remote-debugging-port=9222 &   # or Brave
# log in to SkillRack, then:
python skillrack.py 8820 solution.c
```

## Full Automation with AI

This tool is designed to be used by AI coding agents (Claude Code, opencode, etc.)
for fully autonomous problem solving:

```
Agent (AI) loop:
  1. python skillrack.py --list -m codetrack     →   get unsolved PIDs
  2. python skillrack.py 8820 -r                  →   read problem description
  3. AI writes solution.c                        ←   AI generates the code
  4. python skillrack.py 8820 solution.c          →   submit + run
  5. check result, goto step 2 if failed
```

**You only need to:**
1. Start Chrome with remote debugging
2. Log in to SkillRack
3. Run an AI agent (Claude Code, opencode)

**The AI handles everything else** — reading problems, writing solutions,
iterating on failures. The tool is the "hands" (browser automation),
the AI is the "brain" (code generation + orchestration).

## Language Codes

| Key       | Value | Platform       |
|-----------|-------|----------------|
| `C`       | `2`   | gcc 8.x        |
| `CPP`     | `3`   | C++17          |
| `CPP23`   | `9`   | C++23          |
| `JAVA`    | `1`   | Java 21.0      |
| `PYTHON3` | `7`   | Python 3.12    |

The editor's language `<select>` element is `#langs_input`.

## CLI Reference

```
python skillrack.py <PID> <codeFile> [lang] [flags]

Flags:
  -m, --module      Module: codetrack, dailychallenge, dailytest, codetest
  --port PORT       Chrome debugging port (default 9222)
  -s, --silent      Suppress output
  -i, --interactive Open JS shell on the page
  -r, --read        Read problem description and exit
  -l, --list        List unsolved PIDs in the module
  -a, --auto SCRIPT Auto-complete module (see below)
  --no-run          Paste code but don't click Run

Examples:
  python skillrack.py 8820 solution.c              submit solution
  python skillrack.py 8820 solution.py PYTHON3
  python skillrack.py 8820 -r                       read problem only
  python skillrack.py 8820 -i                       interactive JS shell
  python skillrack.py -m dailychallenge -l          list unsolved DCs
  python skillrack.py -m codetrack -a solver.py     auto-complete
```

## Auto-Complete Mode (`--auto`)

Pass a Python script that exports `generate_code(pid, problem_text)`,
and the tool will iterate every problem in the module, calling your function
for each one:

```python
# solver.py
def generate_code(pid, problem_text):
    # AI writes solution based on problem_text
    return "#include <stdio.h>\nint main() { ... }"
```

```bash
python skillrack.py -m codetrack -a solver.py
```

## How It Works

1. Connects to your Chrome via CDP (`http://127.0.0.1:9222`)
2. Navigates to the problem by PID (direct URL → Solve button → CAPTCHA)
3. **CAPTCHA solving**: Pillow preprocessing (grayscale, contrast, 3x upscale,
   sharpen, threshold) + tesseract with character whitelist + 5 config combos.
   CAPTCHAs are always small addition (answer ≤ 3 digits)
4. Sets language via `#langs_input.value`
5. Pastes code into Ace editor (`#ctracktxtCode`) via `editor.getSession().setValue()`
   — bypasses SkillRack's 30-char diff protection
6. Clicks **Run**
7. Reads results and prints pass/fail summary

## Key Selectors (for troubleshooting)

| Element              | Selector            |
|----------------------|---------------------|
| Language dropdown    | `#langs_input`      |
| Ace editor div       | `#ctracktxtCode`    |
| Hidden textarea      | `#txtCode`          |
| CAPTCHA answer input | `#capval`           |
| Proceed to Solve btn | `#proceedbtn`       |
| Solve button         | `button:has-text("Solve")` |
| Run button           | `button:has-text("Run")`   |
| Save button          | `button:has-text("Save")`  |
| CAPTCHA image        | `img[src*='data:image/png;base64']` |

## Files

- `skillrack.py` — automation script (542 lines, CLI + module API)
- `requirements.txt` — `playwright>=1.40.0`
- `README.md` — this file
