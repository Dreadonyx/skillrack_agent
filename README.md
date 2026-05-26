# SkillRack Automation Agent

Automate SkillRack problem solving using Playwright + Chrome remote debugging.
Paste code, set language, run, and get results — all without manual interaction.

## Requirements

- Node.js 18+
- Google Chrome / Brave running with `--remote-debugging-port=9222`
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed (`apt install tesseract-ocr`)
- Logged-in SkillRack session in the browser

## Quick Start

```bash
# 1. Start Chrome with remote debugging
google-chrome --remote-debugging-port=9222 &

# 2. Log in to SkillRack in that browser

# 3. Install dependencies
cd skillrack-agent
npm install

# 4. Run
node index.js 8820 solution.c
```

## Language Codes

| Key       | Value | Platform       |
|-----------|-------|----------------|
| `C`       | `2`   | gcc 8.x        |
| `CPP`     | `3`   | C++17          |
| `CPP23`   | `9`   | C++23          |
| `JAVA`    | `1`   | Java 21.0      |
| `PYTHON3` | `7`   | Python 3.12    |

The editor's language `<select>` element is `#langs_input`.

## How It Works

1. Connects to your running Chrome via CDP (`http://127.0.0.1:9222`)
2. Finds the SkillRack tab, clicks **Solve** for the given PID
3. Solves the CAPTCHA (OCR on the math-expression image)
4. Clicks **Proceed to Solve** if needed
5. Sets language via `#langs_input.value`
6. Pastes code into the Ace editor (`#ctracktxtCode`) via `editor.getSession().setValue()`
7. Clicks **Run**
8. Reads the results panel and prints pass/fail summary

## CAPTCHA Handling

The CAPTCHA is a simple arithmetic expression (e.g. `25+13`, `9*8`)
rendered as a base64 PNG. The script:

1. Takes an element-level screenshot of the `<img>` tag
2. Runs `tesseract --psm 8` on it
3. Applies a character correction map (`a→4`, `l→1`, `O→0`, `S→5`, etc.)
4. Parses `N op M` and computes the answer
5. Fills `#capval` and clicks **Proceed**

If parsing fails, it falls back to adding the first two digit groups.

If your system's OCR consistently misreads certain characters, tweak the
`cmap` object in `index.js`.

## API

```javascript
const { solveProblem } = require("./index");

const result = await solveProblem("8820", "./solution.c", "C");
console.log(result.passed);   // true / false
console.log(result.text);     // human-readable summary
```

### Options

```javascript
await solveProblem("8820", "./sol.c", "C", {
  chromePort: 9222,        // remote debugging port
  printProgress: true       // log steps to console
});
```

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

## Edge Cases Noted

- SkillRack protects the editor against changes >30 characters by reverting
  to `#txtCode` content. The script bypasses this by calling
  `editor.getSession().setValue()` directly AND firing a `change` event on
  the hidden textarea.
- PrimeFaces overlay elements (`ui-widget-overlay`) sometimes block the
  language selector — the script removes them before setting the language.
- Some problems require clicking **Save** before **Run**; the script tries
  **Run** first and falls back to **Save → Run** if needed.

## Files

- `index.js` — main automation script (CLI + module)
- `package.json` — dependencies (just `playwright`)
- `pid8820.c`, `pid8804.c` — example solutions
- `README.md` — this file

## License

MIT
