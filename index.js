const { chromium } = require("playwright");
const fs = require("fs");
const { execSync } = require("child_process");

// ─── Language codes ───────────────────────────────────────────────
const LANG = { C: "2", CPP: "3", CPP23: "9", JAVA: "1", PYTHON3: "7" };

// ─── Helpers ──────────────────────────────────────────────────────

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

/** Remove PrimeFaces overlay elements that block interaction */
async function removeOverlays(page) {
  await page.evaluate(() => {
    document.querySelectorAll(".ui-widget-overlay, .blockUI, .blockOverlay")
      .forEach(el => el.remove());
  });
}

/** Solve CAPTCHA: find the image, OCR, parse math, fill answer */
async function solveCaptcha(page) {
  const capInput = page.locator("#capval");
  if (!(await capInput.isVisible({ timeout: 1500 }).catch(() => false))) {
    return false;
  }
  console.log("  CAPTCHA detected, solving...");

  // Screenshot the CAPTCHA image element itself
  const capImg = page.locator("img[src*='data:image/png;base64']");
  if (await capImg.isVisible({ timeout: 2000 }).catch(() => false)) {
    await capImg.screenshot({ path: "/tmp/sr_captcha.png" });
  } else {
    await page.screenshot({ path: "/tmp/sr_captcha.png" });
  }

  // OCR
  execSync("tesseract /tmp/sr_captcha.png /tmp/sr_captcha_out --psm 8 2>/dev/null",
    { timeout: 10000 });
  let raw = fs.readFileSync("/tmp/sr_captcha_out.txt", "utf8").trim();
  if (!raw) {
    execSync("tesseract /tmp/sr_captcha.png /tmp/sr_captcha_out --psm 6 2>/dev/null",
      { timeout: 10000 });
    raw = fs.readFileSync("/tmp/sr_captcha_out.txt", "utf8").trim();
  }

  // Character correction (tesseract often misreads digits as letters)
  const cmap = { a: "4", A: "4", l: "1", O: "0", o: "0", S: "5", s: "5",
                 g: "9", r: "1", z: "2", B: "8", b: "6", I: "1", T: "7" };
  for (const [k, v] of Object.entries(cmap)) raw = raw.replaceAll(k, v);
  raw = raw.replace(/[^0-9+\-*xX/]/g, "");

  // Match math expression: number op number
  const m = raw.match(/(\d{1,4})\s*([+\-*xX/])\s*(\d{1,4})/);
  if (m) {
    const a = parseInt(m[1]), op = m[2], b = parseInt(m[3]);
    let ans;
    if (op === "+") ans = a + b;
    else if (op === "-") ans = a - b;
    else if (op === "*" || op === "x" || op === "X") ans = a * b;
    else if (op === "/" && b) ans = Math.floor(a / b);
    if (ans !== undefined && ans >= 0 && ans < 100000) {
      console.log(`  CAPTCHA: ${a} ${op} ${b} = ${ans}`);
      await capInput.fill(String(ans));
      await page.locator("button:has-text('Proceed')").click();
      await sleep(3000);
      return true;
    }
  }

  // Fallback: add first two numbers
  const nums = raw.match(/\d+/g);
  if (nums && nums.length >= 2) {
    const ans = parseInt(nums[0]) + parseInt(nums[1]);
    console.log(`  CAPTCHA (fallback): ${nums[0]}+${nums[1]} = ${ans}`);
    await capInput.fill(String(ans));
    await page.locator("button:has-text('Proceed')").click();
    await sleep(3000);
    return true;
  }

  console.log("  CAPTCHA: could not parse, trying raw:", raw);
  return false;
}

// ─── Main public API ──────────────────────────────────────────────

/**
 * Resolve a problem on SkillRack from a problem-list page:
 * finds the Solve button for the given PID, handles CAPTCHA, sets
 * language, pastes code, runs it, and returns results.
 *
 * @param {string}   pid          – problem ID, e.g. "8820"
 * @param {string}   codeFilePath – path to source file
 * @param {string}   lang         – language key: "C", "CPP", "PYTHON3", "JAVA"
 * @param {object}   opts         – { chromePort, printProgress }
 */
async function solveProblem(pid, codeFilePath, lang = "C", opts = {}) {
  const port = opts.chromePort || 9222;
  const print = opts.printProgress !== false;

  const log = print ? console.log : () => {};

  const code = fs.readFileSync(codeFilePath, "utf8");
  const langVal = LANG[lang.toUpperCase()];
  if (!langVal) throw new Error(`Unknown language "${lang}"`);

  // ── Connect to existing browser ─────────────────────────────────
  log(`Connecting to Chrome on port ${port}...`);
  const browser = await chromium.connectOverCDP(`http://127.0.0.1:${port}`);
  const pages = browser.contexts()[0].pages();
  let page = pages.find(p => p.url().includes("skillrack.com"));
  if (!page) {
    // Open a new page to SkillRack
    page = browser.contexts()[0].pages()[0] || (await browser.contexts()[0].newPage());
  }
  await page.bringToFront();

  // ── Ensure we are on a page that shows the editor ───────────────
  const onProblemPage = () =>
    page.evaluate(() => !!document.querySelector(".ace_editor"))
      .catch(() => false);

  if (!(await onProblemPage())) {
    // Might be on the challenge list or problem description page
    const hasProceed = await page.locator("#proceedbtn")
      .isVisible({ timeout: 1000 }).catch(() => false);
    const hasSolve = await page.locator("button:has-text('Solve')")
      .first().isVisible({ timeout: 1000 }).catch(() => false);

    if (hasSolve) {
      log("Clicking Solve button...");
      const btns = await page.locator("button:has-text('Solve')").all();
      for (const btn of btns) {
        const parent = await btn.evaluate(el => {
          const p = el.closest("tr,div,li,table");
          return p ? p.textContent : "";
        });
        if (parent.includes(pid)) {
          await btn.click();
          break;
        }
      }
      await sleep(2000);
      // After Solve → CAPTCHA may appear
      await solveCaptcha(page);
      if (await page.locator("#proceedbtn")
            .isVisible({ timeout: 2000 }).catch(() => false)) {
        log("Clicking Proceed to Solve...");
        await page.locator("#proceedbtn").click();
        await sleep(1500);
        await solveCaptcha(page);
      }
    } else if (hasProceed) {
      log("Clicking Proceed to Solve...");
      await page.locator("#proceedbtn").click();
      await sleep(1500);
      await solveCaptcha(page);
    } else {
      // Try navigating directly
      log("Navigating to SkillRack...");
      await page.goto("https://skillrack.com", { waitUntil: "networkidle", timeout: 15000 });
      await sleep(2000);
    }

    // Wait for editor to appear
    for (let i = 0; i < 20; i++) {
      if (await onProblemPage()) break;
      await sleep(1000);
    }
  }

  if (!(await onProblemPage())) {
    throw new Error("Could not load editor page after multiple attempts");
  }
  log("Editor loaded.");

  // ── Remove overlays ─────────────────────────────────────────────
  await removeOverlays(page);
  await sleep(300);

  // ── Set language ────────────────────────────────────────────────
  log(`Setting language to ${lang} (value=${langVal})...`);
  await page.evaluate((v) => {
    const sel = document.querySelector("#langs_input");
    if (sel) { sel.value = v; sel.dispatchEvent(new Event("change")); }
  }, langVal);
  await sleep(500);

  // ── Paste code ──────────────────────────────────────────────────
  log(`Pasting code (${code.length} bytes)...`);
  await page.evaluate((c) => {
    // Update the hidden textarea (required by SkillRack's change detector)
    const ta = document.getElementById("txtCode");
    if (ta) ta.value = c;
    // Use Ace session API directly (bypasses the 30-char diff guard)
    const editor = window.ace.edit("ctracktxtCode");
    editor.getSession().setValue(c);
    // Fire change on textarea so the page knows it should be saved
    if (ta) ta.dispatchEvent(new Event("change", { bubbles: true }));
  }, code);
  await sleep(1000);

  // ── Run ─────────────────────────────────────────────────────────
  const runBtn = page.locator("button:has-text('Run')");
  if (!(await runBtn.isVisible({ timeout: 3000 }).catch(() => false))) {
    // Maybe there is both a Save and Run button; click Save first
    const saveBtn = page.locator("button:has-text('Save')");
    if (await saveBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
      log("Saving first...");
      await saveBtn.click();
      await sleep(2000);
    }
  }

  log("Clicking Run...");
  await runBtn.click();
  log("Waiting for results...");
  await sleep(6000);

  // ── Detect results ──────────────────────────────────────────────
  let resultText;
  for (let i = 0; i < 10; i++) {
    resultText = await page.evaluate(() => document.body.textContent);
    if (resultText.includes("Passed") || resultText.includes("Failed") ||
        resultText.includes("did not pass")) break;
    await sleep(1000);
  }

  const summary = parseResult(resultText);

  log("");
  log("─── Result ───────────────────────────────────────");
  log(summary.text);

  await browser.close();
  return summary;
}

function parseResult(body) {
  if (body.includes("Passed all test cases")) {
    return { passed: true, text: "ALL TEST CASES PASSED" };
  }
  const pm = body.match(/(\d+)\s*Passed/);
  const fm = body.match(/(\d+)\s*Private/);
  if (pm || fm) {
    const parts = [];
    if (pm) parts.push(pm[1] + " Passed");
    if (fm) parts.push(fm[1] + " Failed (hidden)");
    const allPassed = fm === null;
    return { passed: allPassed, text: parts.join(", ") };
  }
  if (body.includes("Code did not pass")) {
    return { passed: false, text: "Code did not pass execution (compile/runtime error)" };
  }
  return { passed: false, text: "Unknown result" };
}

// ─── CLI entry point ──────────────────────────────────────────────
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log(`
Usage: node index.js <PID> <codeFile> [language]

Languages: C, CPP, JAVA, PYTHON3  (default: C)

Examples:
  node index.js 8820 solution.c
  node index.js 8804 solution.py PYTHON3
`);
    process.exit(1);
  }
  const [pid, codeFile, lang] = args;
  solveProblem(pid, codeFile, lang || "C")
    .then(s => {
      console.log(s.passed ? "\n✓ Done" : "\n✗ Done (some tests failed)");
      process.exit(s.passed ? 0 : 1);
    })
    .catch(e => {
      console.error("\nError:", e.message);
      process.exit(1);
    });
}

module.exports = { solveProblem, solveCaptcha, LANG, parseResult };
