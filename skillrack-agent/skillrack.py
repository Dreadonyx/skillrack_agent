import sys, os, re, subprocess, time, argparse, base64, io

LANG = {
    "C": "2", "CPP": "3", "CPP23": "9",
    "JAVA": "1", "PYTHON3": "7",
}

SECTION = {
    "course":      0,
    "starter":     1,
    "very-easy":   2,
    "easy":        3,
    "average":     4,
}

SECTION_LABEL = {
    "course":    "Programming Course",
    "starter":   "STARTER",
    "very-easy": "VERY-EASY",
    "easy":      "EASY",
    "average":   "AVERAGE",
}

# ─── Utilities ────────────────────────────────────────────────────

def sleep(ms):
    time.sleep(ms / 1000)

def log(msg, silent=False):
    if not silent:
        print(msg)

def remove_overlays(page):
    page.evaluate("""() => {
        document.querySelectorAll(".ui-widget-overlay, .blockUI, .blockOverlay")
            .forEach(el => el.remove());
    }""")

def ensure_page(context):
    for p in context.pages:
        if "skillrack.com" in p.url:
            p.bring_to_front()
            return p
    p = context.pages[0] if context.pages else context.new_page()
    p.bring_to_front()
    return p

def wait_for_url(page, target_substring, timeout=10):
    for _ in range(timeout):
        if target_substring in page.url:
            return True
        sleep(1000)
    return False

# ─── Error Recovery ───────────────────────────────────────────────

def go_home(page):
    log("  Going back to home...")
    page.goto("https://skillrack.com/faces/ui/profile.xhtml",
              wait_until="domcontentloaded", timeout=15000)
    sleep(2000)
    remove_overlays(page)

def go_programming(page):
    log("  Going to Programming...")
    page.goto("https://skillrack.com/faces/candidate/trackshome.xhtml",
              wait_until="domcontentloaded", timeout=15000)
    sleep(2000)
    remove_overlays(page)

def go_level1(page):
    log("  Going to Level 1...")
    page.goto("https://skillrack.com/faces/candidate/lev1.xhtml",
              wait_until="domcontentloaded", timeout=15000)
    sleep(2000)
    remove_overlays(page)

def is_logged_out(page):
    return page.evaluate("""() => {
        const t = document.body.innerText;
        const has_login_form = document.querySelector('input[type=password]') !== null ||
                                document.querySelector('#loginForm') !== null ||
                                document.querySelector('form[action*=\"login\"]') !== null;
        if (has_login_form) return true;
        if (/Sign[\\s-]in/i.test(t) && !/Previous Login/i.test(t)) return true;
        if (/Sign[\\s-]up/i.test(t)) return true;
        return false;
    }""")

def recover(page, target_func, max_retries=3):
    """Wrapped navigation: go home → try again on failure."""
    for attempt in range(max_retries):
        try:
            if is_logged_out(page):
                log("LOGGED OUT — user must log in first", silent=False)
                return False
            if target_func():
                return True
        except Exception as e:
            log(f"  Attempt {attempt+1} failed: {e}")
        if attempt < max_retries - 1:
            go_home(page)
    return False

# ─── CAPTCHA ──────────────────────────────────────────────────────

def _captcha_image(page):
    b64 = page.evaluate("""() => {
        const i = document.querySelector('#j_id_75');
        return i ? i.src : null;
    }""")
    if not b64 or "base64" not in b64:
        return None
    from PIL import Image
    raw = base64.b64decode(b64.split(",")[1] + "==")
    return Image.open(io.BytesIO(raw)).convert("L")

def _captcha_ocr(img):
    from PIL import Image, ImageOps, ImageFilter
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.resize((img.width * 4, img.height * 4), Image.LANCZOS)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageOps.invert(img)
    img.save("/tmp/sr_cap.png")

    results = set()
    for psm in ["6", "8", "7"]:
        try:
            subprocess.run(["tesseract", "/tmp/sr_cap.png", "/tmp/sr_o",
                           "--psm", psm, "--oem", "3",
                           "-c", "tessedit_char_whitelist=0123456789+*"],
                          capture_output=True, timeout=10)
            lines = [l.strip() for l in open("/tmp/sr_o.txt").read().split("\n") if l.strip()]
            txt = lines[-1] if lines else ""
            if txt:
                cmap = {"O":"0","S":"5","s":"5","l":"1","I":"1",
                        "B":"8","b":"6","g":"9","q":"9","T":"7","Z":"2","z":"2"}
                for k, v in cmap.items(): txt = txt.replace(k, v)
                txt = re.sub(r"[^0-9+]", "", txt)
                results.add(txt)
        except Exception:
            continue
    return results

def _parse_captcha(raw):
    """Extract N+N addition from OCR text (always simple addition)."""
    if "+" not in raw:
        nums = re.findall(r"\d+", raw)
        if len(nums) >= 2:
            return int(nums[-2]) + int(nums[-1])
        return None
    parts = raw.split("+")
    left = re.findall(r"\d+", parts[0])
    right = re.findall(r"\d+", parts[1])
    a = next((int(d) for d in reversed(left) if len(d) <= 3), None)
    b = next((int(d) for d in right if len(d) <= 3), None)
    if a is not None and b is not None:
        return a + b
    if left and right:
        return int(left[-1]) + int(right[0])
    return None

def solve_captcha(page, silent=False):
    cap = page.locator("#capval")
    if not cap.is_visible(timeout=1500):
        return False
    log("  CAPTCHA detected, solving...", silent)

    for attempt in range(3):
        img = _captcha_image(page)
        if img is None:
            log("  No CAPTCHA image found, retrying...", silent)
            sleep(2000)
            continue
        results = _captcha_ocr(img)
        for raw in results:
            ans = _parse_captcha(raw)
            if ans is not None and 0 <= ans <= 999:
                log(f"  CAPTCHA: {ans} (raw: {raw})", silent)
                cap.fill(str(ans))
                sleep(500)
                return True
        if attempt < 2:
            log(f"  CAPTCHA retry {attempt+2}/3...", silent)
            sleep(2000)
    log(f"  CAPTCHA failed: {results}", silent)
    return False

# ─── Navigation — Home → Programming → Level 1 → Section → Language → Part ──

def _click_nav(page, text, url_substr):
    for btn in page.locator(f"a:has-text('{text}'), button:has-text('{text}')").all():
        if btn.is_visible(timeout=1000):
            btn.click()
            sleep(3000)
            return url_substr in page.url
    return False

def nav_home_to_programming(page):
    if "trackshome" in page.url:
        return True
    go_home(page)
    return recover(page, lambda: _click_nav(page, "Programming", "trackshome"))

def nav_programming_to_level1(page):
    if "lev1" in page.url:
        return True
    go_programming(page)
    for _ in range(5):
        for btn in page.locator("button:has-text('View'), a:has-text('View')").all():
            parent = btn.evaluate("el => (el.closest('div,tr,td,li') || el).innerText")
            if "Level 1" in parent or "Level" in parent:
                btn.click()
                sleep(3000)
                if "lev1" in page.url:
                    return True
                break
        sleep(1000)
    return "lev1" in page.url

def nav_level1_to_codetutor(page):
    if "codeprogramgroup" in page.url and "CODETUTOR" in page.url:
        return True
    go_level1(page)
    for _ in range(8):
        for btn in page.locator("button:has-text('View'), a:has-text('View')").all():
            parent = btn.evaluate("el => (el.closest('div,tr,td,li') || el).innerText")
            if "Learn C" in parent or "Java" in parent or "Python" in parent or "SQL" in parent:
                btn.click()
                sleep(3000)
                if "CODETUTOR" in page.url:
                    return True
                break
        sleep(1000)
    return "CODETUTOR" in page.url

def nav_codetutor_show_language(page, lang="Python"):
    idx = {"C": 0, "Java": 1, "Python": 2, "C++": 3, "SQL": 4,
           "Data Structures in C": 5, "Data Structures in Java": 6}.get(lang, 2)
    btn_id = f"#pkglistform\\:cttbl\\:{idx}\\:j_id_41"
    btn = page.locator(btn_id)
    if btn.is_visible(timeout=3000):
        btn.click()
        sleep(2000)
        return True
    log(f"  Language '{lang}' show button not found")
    return False

def nav_codetutor_show_section(page, section="easy"):
    idx = SECTION.get(section, 3)
    label = SECTION_LABEL.get(section, "EASY")
    for attempt in range(5):
        btn_id = f"#pkglistform\\:j_id_49\\:{idx}\\:j_id_4h"
        btn = page.locator(btn_id)
        if btn.is_visible(timeout=2000):
            btn.click()
            sleep(2000)
            return True
        # Try finding by text
        for el in page.locator("button:has-text('Show')").all():
            parent = el.evaluate("el => (el.closest('div,tr,td,li') || el).innerText")
            if label in parent:
                el.click()
                sleep(2000)
                return True
        sleep(1000)
    log(f"  Section '{section}' not found")
    return False

def nav_codetutor_open_part(page, part_idx=0):
    btn_id = f"#cttbl\\:{part_idx}\\:j_id_4u"
    btn = page.locator(btn_id)
    if btn.is_visible(timeout=2000):
        btn.click()
        sleep(2000)
        return True
    return False

def nav_codetutor_click_solve(page, pid):
    for btn in page.locator("button:has-text('Solve')").all():
        parent = btn.evaluate("el => (el.closest('div,tr,td,li,table') || el).innerText")
        if pid in parent:
            btn.click()
            sleep(4000)
            return True
    return False

def navigate_to_problem(page, pid, language="Python", section="easy"):
    """
    Full navigation pipeline:
    Home → Programming → Level 1 → Learn C, Java... → CODETUTOR →
    Show Language → Show Section → Open Part → Click Solve
    """
    if not nav_home_to_programming(page):
        raise RuntimeError("Could not reach Programming page")
    if not nav_programming_to_level1(page):
        raise RuntimeError("Could not reach Level 1")
    if not nav_level1_to_codetutor(page):
        raise RuntimeError("Could not reach CodeTutor")
    if not nav_codetutor_show_language(page, language):
        raise RuntimeError(f"Could not show language '{language}'")
    if not nav_codetutor_show_section(page, section):
        raise RuntimeError(f"Could not show section '{section}'")

    # Walk through parts until we find the PID
    for part_idx in range(10):
        view_btn = page.locator(f"#cttbl\\:{part_idx}\\:j_id_4u")
        if not view_btn.is_visible(timeout=1000):
            # Check if problems are already visible
            if nav_codetutor_click_solve(page, pid):
                return True
            break
        view_btn.click()
        sleep(2000)
        if nav_codetutor_click_solve(page, pid):
            return True
        log(f"  PID {pid} not in part {part_idx+1}")

    raise RuntimeError(f"PID {pid} not found in any part")

# ─── Editor actions ───────────────────────────────────────────────

def handle_captcha_and_proceed(page, silent=False):
    """CAPTCHA is already on page → solve it → click Proceed."""
    if page.locator("#capval").is_visible(timeout=2000):
        solve_captcha(page, silent)
    if page.locator("#proceedbtn").is_visible(timeout=3000):
        log("Clicking Proceed...", silent)
        page.locator("#proceedbtn").click()
        sleep(3000)

def set_language(page, lang, silent=False):
    lang_val = LANG.get(lang.upper())
    if not lang_val:
        raise ValueError(f"Unknown language: {lang}")
    log(f"Setting language to {lang}", silent)
    page.evaluate("""(v) => {
        const sel = document.querySelector('#langs_input');
        if (sel) { sel.value = v; sel.dispatchEvent(new Event('change')); }
    }""", lang_val)
    sleep(500)

def paste_code(page, code, silent=False):
    log(f"Pasting code ({len(code)} bytes)...", silent)
    page.evaluate("""(c) => {
        const ta = document.getElementById('txtCode');
        if (ta) ta.value = c;
        const editor = window.ace.edit('ctracktxtCode');
        editor.getSession().setValue(c);
        if (ta) ta.dispatchEvent(new Event('change', { bubbles: true }));
    }""", code)
    sleep(1000)

def click_run(page, silent=False):
    run = page.locator("button:has-text('Run')")
    if not run.is_visible(timeout=3000):
        save = page.locator("button:has-text('Save')")
        if save.is_visible(timeout=1000):
            log("Saving first...", silent)
            save.click()
            sleep(2000)
    log("Clicking Run...", silent)
    run.click()
    log("Waiting for results...", silent)
    sleep(6000)

    for _ in range(15):
        text = page.evaluate("() => document.body.innerText")
        if any(x in text.lower() for x in ("passed", "failed", "did not pass",
                                            "error", "compilation")):
            return text
        panel = page.evaluate("""() => {
            const el = document.querySelector('[id*=\"result\"], [id*=\"output\"], .ui-outputpanel');
            return el ? el.innerText : '';
        }""")
        if panel and any(x in panel.lower() for x in ("passed", "failed", "error")):
            return text
        sleep(1000)
    return page.evaluate("() => document.body.innerText")

# ─── Results ──────────────────────────────────────────────────────

def parse_result(body):
    b = body.lower()
    if any(x in b for x in ("passed all", "test case passed", "all test case")):
        return {"passed": True, "text": "ALL TEST CASES PASSED"}
    pm = re.search(r"(\d+)\s*[Pp]assed", body)
    fm = re.search(r"(\d+)\s*[Pp]rivate", body)
    hm = re.search(r"(\d+)\s*[Hh]idden", body)
    if pm or fm or hm:
        parts = []
        if pm: parts.append(f"{pm[1]} Passed")
        fc = None
        if fm: fc = int(fm[1])
        if hm and fc is None: fc = int(hm[1])
        if fc: parts.append(f"{fc} Failed (hidden)")
        return {"passed": fc is None, "text": ", ".join(parts)}
    if "compilation error" in b or "syntax error" in b:
        return {"passed": False, "text": "Compilation error"}
    if "time limit" in b:
        return {"passed": False, "text": "Time limit exceeded"}
    if "did not pass" in b:
        return {"passed": False, "text": "Test cases failed (wrong output)"}
    if "runtime error" in b:
        return {"passed": False, "text": "Runtime error"}
    tm = re.search(r"(\d+)\s*/\s*(\d+)", body)
    if tm:
        return {"passed": tm[1] == tm[2], "text": f"{tm[1]}/{tm[2]} test cases passed"}
    return {"passed": False, "text": "Unknown result"}

# ─── High-level API ───────────────────────────────────────────────

def solve_problem(pid, code_file=None, lang="PYTHON3",
                  language="Python", section="easy",
                  chrome_port=9222, silent=False, run_only=True):
    log = print if not silent else lambda *a, **kw: None
    code = None
    if code_file:
        with open(code_file) as f:
            code = f.read()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{chrome_port}")
        page = ensure_page(browser.contexts[0])
        remove_overlays(page)

        if is_logged_out(page):
            log("LOGGED OUT — please log in to SkillRack first")
            browser.close()
            return {"passed": False, "text": "Not logged in"}

        # Navigate
        try:
            navigate_to_problem(page, pid, language, section)
        except RuntimeError as e:
            log(f"Navigation failed: {e}")
            browser.close()
            return {"passed": False, "text": f"Navigation failed: {e}"}

        # CAPTCHA → Proceed
        handle_captcha_and_proceed(page, silent)

        # Wait for editor
        for _ in range(20):
            if page.evaluate("() => !!document.querySelector('.ace_editor')"):
                break
            sleep(1000)

        if not page.evaluate("() => !!document.querySelector('.ace_editor')"):
            log("Editor not loaded after CAPTCHA")
            browser.close()
            return {"passed": False, "text": "Editor did not load"}

        log("Editor loaded.")
        remove_overlays(page)

        if code:
            set_language(page, lang, silent)
            paste_code(page, code, silent)

        if code and run_only:
            text = click_run(page, silent)
            result = parse_result(text)
            log("")
            log("─── Result ───────────────────────────────────────")
            log(result["text"])
            browser.close()
            return result

        browser.close()
        return {"passed": None, "text": "Code pasted (Run skipped)"}

def read_problem(pid, language="Python", section="easy",
                 chrome_port=9222, silent=False):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{chrome_port}")
        page = ensure_page(browser.contexts[0])
        remove_overlays(page)
        try:
            navigate_to_problem(page, pid, language, section)
        except RuntimeError as e:
            browser.close()
            return {"title": "", "text": f"Navigation failed: {e}"}
        handle_captcha_and_proceed(page, silent)
        sleep(3000)
        text = page.evaluate("() => document.body.innerText")
        browser.close()
        return {"title": pid, "text": text[:3000]}

# ─── CLI ──────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="SkillRack automation — full pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python skillrack.py 2598 solution.py --section easy --language Python
  python skillrack.py 2598 solution.py -s easy -l PYTHON3
  python skillrack.py 2598 --read -s easy          # read problem only
        """)
    ap.add_argument("pid", nargs="?", help="Problem ID")
    ap.add_argument("code_file", nargs="?", default=None, help="Solution file")
    ap.add_argument("lang", nargs="?", default="PYTHON3",
                    help="Language: C, CPP, JAVA, PYTHON3")
    ap.add_argument("--language", default="Python",
                    help="Programming language on CodeTutor: C, Java, Python, C++, SQL")
    ap.add_argument("--section", "-s", default="easy",
                    choices=list(SECTION.keys()),
                    help="Section: course, starter, very-easy, easy, average")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--silent", "-q", action="store_true")
    ap.add_argument("--read", "-r", action="store_true")
    ap.add_argument("--no-run", dest="run_only", action="store_false", default=True)
    args = ap.parse_args()

    if not args.pid:
        ap.error("pid is required")

    try:
        if args.read:
            prob = read_problem(args.pid, args.language, args.section,
                                args.port, args.silent)
            print(f"Problem {args.pid}:")
            print(prob["text"][:2000])
            return

        result = solve_problem(args.pid, args.code_file, args.lang,
                               args.language, args.section,
                               args.port, args.silent, args.run_only)
        if result["passed"] is not None:
            print(f"\n{'✓' if result['passed'] else '✗'} Done — {result['text']}")
            sys.exit(0 if result["passed"] else 1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
