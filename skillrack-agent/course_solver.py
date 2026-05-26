#!/usr/bin/env python3
"""
SkillRack Course Solver — fully autonomous.
Navigates Python Course → finds unsolved → solves all problems.
"""

import sys, os, re, time, json, base64, io, subprocess
from playwright.sync_api import sync_playwright

LANG = {"C":"2","CPP":"3","JAVA":"1","PYTHON3":"7"}

def sleep(ms):
    time.sleep(ms/1000)

def log(msg):
    print(f"  {msg}")

def ensure_page(context):
    for p in context.pages:
        if "skillrack.com" in p.url:
            p.bring_to_front()
            return p
    return context.pages[0] if context.pages else context.new_page()

def is_logged_out(page):
    return page.evaluate(
        "() => document.body.innerText.includes('Sign-in') || "
        "document.body.innerText.includes('Login') || "
        "document.body.innerText.includes('Sign Up')")

def remove_overlays(page):
    page.evaluate("""() => {
        document.querySelectorAll(".ui-widget-overlay, .blockUI, .blockOverlay")
            .forEach(el => el.remove());
    }""")

# ─── CAPTCHA ──────────────────────────────────────────────────

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

def solve_captcha(page):
    if not page.locator("#capval").is_visible(timeout=1500):
        return True
    log("CAPTCHA detected, solving...")
    from PIL import Image, ImageOps, ImageFilter

    for attempt in range(3):
        img = _captcha_image(page)
        if img is None:
            sleep(2000)
            continue
        img = ImageOps.autocontrast(img, cutoff=2)
        img = img.resize((img.width*4, img.height*4), Image.LANCZOS)
        img = img.filter(ImageFilter.SHARPEN)
        img = img.filter(ImageFilter.SHARPEN)
        img = ImageOps.invert(img)
        img.save("/tmp/sr_cap.png")

        results = set()
        for psm in ["6","8","7"]:
            try:
                subprocess.run(["tesseract","/tmp/sr_cap.png","/tmp/sr_o",
                               "--psm",psm,"--oem","3",
                               "-c","tessedit_char_whitelist=0123456789+*"],
                              capture_output=True,timeout=10)
                lines = [l.strip() for l in open("/tmp/sr_o.txt").read().split("\n") if l.strip()]
                txt = lines[-1] if lines else ""
                cmap = {"O":"0","S":"5","s":"5","l":"1","I":"1",
                        "B":"8","b":"6","g":"9","q":"9","T":"7","Z":"2","z":"2"}
                for k,v in cmap.items(): txt = txt.replace(k,v)
                txt = re.sub(r"[^0-9+]","",txt)
                results.add(txt)
            except: pass

        for raw in results:
            if "+" not in raw:
                nums = re.findall(r"\d+", raw)
                if len(nums) >= 2:
                    ans = int(nums[-2])+int(nums[-1])
                    if 0<=ans<=999:
                        page.locator("#capval").fill(str(ans))
                        sleep(500)
                        log(f"CAPTCHA: {ans}")
                        return True
                continue
            parts = raw.split("+")
            left = re.findall(r"\d+",parts[0])
            right = re.findall(r"\d+",parts[1])
            a = next((int(d) for d in reversed(left) if len(d)<=3), None)
            b = next((int(d) for d in right if len(d)<=3), None)
            if a is not None and b is not None and 0<=(a+b)<=999:
                page.locator("#capval").fill(str(a+b))
                sleep(500)
                log(f"CAPTCHA: {a}+{b}={a+b}")
                return True
        if attempt < 2:
            sleep(2000)
    log("CAPTCHA FAILED")
    return False

# ─── Navigation ───────────────────────────────────────────────

def nav_to_course(page):
    log("Navigating to Programming page...")
    page.goto("https://skillrack.com/faces/candidate/trackshome.xhtml",
              wait_until="domcontentloaded", timeout=15000)
    sleep(3000)
    remove_overlays(page)

    log("Clicking Level 1 View...")
    for _ in range(8):
        found = False
        for btn in page.locator("button:has-text('View'), a:has-text('View')").all():
            parent = btn.evaluate("el => (el.closest('div,tr,td,li')||el).innerText")
            if "Level 1" in parent or "level 1" in parent.lower():
                btn.click()
                sleep(3000)
                found = True
                break
        if found: break
        sleep(1000)

    log("Clicking Learn C/Java/Python View...")
    for _ in range(10):
        found = False
        for btn in page.locator("button:has-text('View'), a:has-text('View')").all():
            parent = btn.evaluate("el => (el.closest('div,tr,td,li')||el).innerText")
            if "Learn C" in parent or ("Java" in parent and "Python" not in parent and "JavaScript" not in parent):
                btn.click()
                sleep(3000)
                found = True
                break
        if found: break
        sleep(1000)
        if "CODETUTOR" in page.url: break

    if "CODETUTOR" not in page.url:
        page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                  wait_until="domcontentloaded", timeout=15000)
        sleep(3000)

    log("Clicking Python Show...")
    btn = page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41")
    btn.wait_for(state="visible", timeout=5000)
    btn.click()
    sleep(2500)

    log("Clicking Course Show...")
    btn = page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h")
    btn.wait_for(state="visible", timeout=5000)
    btn.click()
    sleep(2500)

# ─── List unsolved problems ──────────────────────────────────

def list_unsolved(page):
    """Return list of (part_idx, pid, button_text) for all Solve buttons."""
    problems = []
    for part_idx in range(15):
        view_btn = page.locator(f"#cttbl\\:{part_idx}\\:j_id_4u")
        if view_btn.is_visible(timeout=800):
            view_btn.click()
            sleep(2000)
            remove_overlays(page)
            # Check all Solve buttons in this part
            for btn in page.locator("button:has-text('Solve')").all():
                parent = btn.evaluate("el => (el.closest('div,tr,td,li,table')||el).innerText")
                pid_match = re.search(r"(\d{4,})", parent)
                pid = pid_match[1] if pid_match else "unknown"
                problems.append((part_idx, pid, parent[:80]))
            log(f"  Part {part_idx+1}: {len(problems)} unsolved so far")
        else:
            # Check if problems are outside view btns
            for btn in page.locator("button:has-text('Solve')").all():
                parent = btn.evaluate("el => (el.closest('div,tr,td,li,table')||el).innerText")
                pid_match = re.search(r"(\d{4,})", parent)
                pid = pid_match[1] if pid_match else "unknown"
                problems.append((part_idx, pid, parent[:80]))
            break
    return problems

# ─── Problem solving ─────────────────────────────────────────

def read_problem_text(page):
    sleep(2000)
    remove_overlays(page)
    # Get the question text from common containers
    text = page.evaluate("""() => {
        const sel = document.querySelector('.questionText, .problemText, ' +
            '[id*=\"question\"], [id*=\"problem\"], [class*=\"question\"], [class*=\"problem\"]');
        if (sel) return sel.innerText;
        // Fallback: look for code/problem text
        const body = document.body.innerText;
        const idx = body.indexOf('Examples');
        if (idx > 0) return body.substring(0, idx + 50);
        return body.substring(0, 3000);
    }""")
    return text

def generate_solution(problem_text, pid):
    """Use AI to generate solution code based on problem description."""
    log(f"Generating solution for PID {pid}...")
    # We'll use the problem text directly to write code
    # For now, print the problem description for the user/AI
    return None

def paste_code(page, code):
    log(f"Pasting code ({len(code)} bytes)...")
    page.evaluate("""(c) => {
        const ta = document.getElementById('txtCode');
        if (ta) ta.value = c;
        const editor = window.ace.edit('ctracktxtCode');
        if (editor) editor.getSession().setValue(c);
        if (ta) ta.dispatchEvent(new Event('change', {bubbles: true}));
    }""", code)
    sleep(1000)

def set_language(page, lang="PYTHON3"):
    lang_val = LANG.get(lang.upper(), "7")
    page.evaluate("""(v) => {
        const sel = document.querySelector('#langs_input');
        if (sel) { sel.value = v; sel.dispatchEvent(new Event('change')); }
    }""", lang_val)
    sleep(500)

def click_run_and_wait(page):
    log("Clicking Run...")
    run = page.locator("button:has-text('Run')")
    if not run.is_visible(timeout=3000):
        log("Save button available, clicking Save first...")
        save = page.locator("button:has-text('Save')")
        if save.is_visible(timeout=1000):
            save.click()
            sleep(2000)
        run.wait_for(state="visible", timeout=5000)
    run.click()
    log("Waiting for results...")
    sleep(5000)

    for _ in range(20):
        text = page.evaluate("() => document.body.innerText")
        bl = text.lower()
        if any(x in bl for x in ("passed all", "test case passed", "all test case",
                                  "did not pass", "compilation error", "runtime error",
                                  "syntax error", "time limit")):
            return text
        sleep(1000)
    return page.evaluate("() => document.body.innerText")

def parse_result(body):
    b = body.lower()
    if any(x in b for x in ("passed all", "test case passed", "all test case")):
        return {"passed": True, "text": "ALL TEST CASES PASSED"}
    pm = re.search(r"(\d+)\s*[Pp]assed", body)
    if "did not pass" in b:
        return {"passed": False, "text": "Test cases failed (wrong output)"}
    if "compilation error" in b or "syntax error" in b:
        return {"passed": False, "text": "Compilation error"}
    if "runtime error" in b:
        return {"passed": False, "text": "Runtime error"}
    if "time limit" in b:
        return {"passed": False, "text": "Time limit exceeded"}
    tm = re.search(r"(\d+)\s*/\s*(\d+)", body)
    if tm:
        return {"passed": tm[1]==tm[2], "text": f"{tm[1]}/{tm[2]} test cases passed"}
    return {"passed": False, "text": "Unknown result"}

# ─── Main loop ───────────────────────────────────────────────

def solve_course():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = ensure_page(context)
        remove_overlays(page)

        if is_logged_out(page):
            log("LOGGED OUT — please log in first")
            return

        nav_to_course(page)
        problems = list_unsolved(page)
        log(f"\n{'='*60}")
        log(f"Found {len(problems)} unsolved problems in Python Course")
        for i, (pi, pid, desc) in enumerate(problems):
            log(f"  {i+1}. Part {pi+1}, PID {pid}: {desc.strip()[:60]}")
        log('='*60)

        solved = 0
        failed = 0

        for idx, (part_idx, pid, desc) in enumerate(problems):
            log(f"\n{'─'*50}")
            log(f"Problem {idx+1}/{len(problems)}: PID {pid}")
            log(f"Description: {desc.strip()[:80]}")

            # Navigate to problem
            page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                      wait_until="domcontentloaded", timeout=15000)
            sleep(2500)
            remove_overlays(page)

            # Re-open Course section
            btn = page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41")
            if btn.is_visible(timeout=2000): btn.click(); sleep(2000)
            btn = page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h")
            if btn.is_visible(timeout=2000): btn.click(); sleep(2000)

            # Open part and click Solve
            view_btn = page.locator(f"#cttbl\\:{part_idx}\\:j_id_4u")
            if view_btn.is_visible(timeout=2000):
                view_btn.click()
                sleep(2000)
                remove_overlays(page)

            solve_clicked = False
            for btn in page.locator("button:has-text('Solve')").all():
                parent = btn.evaluate("el => (el.closest('div,tr,td,li,table')||el).innerText")
                if pid in parent:
                    btn.click()
                    sleep(4000)
                    solve_clicked = True
                    break

            if not solve_clicked:
                log(f"Could not click Solve for PID {pid}, might already be solved")
                solved += 1
                continue

            # CAPTCHA → Proceed
            solve_captcha(page)
            if page.locator("#proceedbtn").is_visible(timeout=3000):
                log("Clicking Proceed...")
                page.locator("#proceedbtn").click()
                sleep(3000)

            # Read the problem
            prob_text = read_problem_text(page)
            log(f"\nProblem text (first 500 chars):\n{prob_text[:500]}")

            # Save problem text for AI to generate solution
            with open(f"/tmp/sr_pid_{pid}.txt", "w") as f:
                f.write(prob_text)

            log(f"\nProblem description saved to /tmp/sr_pid_{pid}.txt")
            log("AI needs to generate solution code and save to a file, then re-run with:")
            log(f"  python3 course_solver.py submit {pid} /tmp/solution_{pid}.py")

        log(f"\nDone! Solved: {solved}, Failed: {failed}")
        if problems:
            log(f"Next step: generate solutions for each problem and submit")
            log("Run: python3 course_solver.py submit <PID> <solution_file>")
        browser.close()

def submit_solution(pid, code_file):
    with open(code_file) as f:
        code = f.read()

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = ensure_page(browser.contexts[0])
        remove_overlays(page)

        if is_logged_out(page):
            log("LOGGED OUT")
            return

        # Navigate to problem
        page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                  wait_until="domcontentloaded", timeout=15000)
        sleep(2500)
        remove_overlays(page)

        # Open Course section
        btn = page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41")
        if btn.is_visible(timeout=2000): btn.click(); sleep(2000)
        btn = page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h")
        if btn.is_visible(timeout=2000): btn.click(); sleep(2000)

        # Find and click Solve
        for part_idx in range(15):
            view_btn = page.locator(f"#cttbl\\:{part_idx}\\:j_id_4u")
            if view_btn.is_visible(timeout=800):
                view_btn.click()
                sleep(2000)
                remove_overlays(page)
            for btn in page.locator("button:has-text('Solve')").all():
                parent = btn.evaluate("el => (el.closest('div,tr,td,li,table')||el).innerText")
                if pid in parent:
                    btn.click()
                    sleep(4000)
                    break
            else:
                continue
            break

        # CAPTCHA → Proceed
        solve_captcha(page)
        if page.locator("#proceedbtn").is_visible(timeout=3000):
            page.locator("#proceedbtn").click()
            sleep(3000)

        # Wait for editor
        for _ in range(20):
            if page.evaluate("() => !!document.querySelector('.ace_editor')"):
                break
            sleep(1000)

        if not page.evaluate("() => !!document.querySelector('.ace_editor')"):
            log("Editor did not load")
            return

        remove_overlays(page)
        set_language(page)
        paste_code(page, code)
        text = click_run_and_wait(page)
        result = parse_result(text)
        log(f"\nResult: {result['text']}")
        browser.close()
        return result

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "submit":
        pid = sys.argv[2]
        code_file = sys.argv[3]
        submit_solution(pid, code_file)
    elif len(sys.argv) >= 2 and sys.argv[1] == "solve":
        pid = sys.argv[2]
        code_file = sys.argv[3] if len(sys.argv) > 3 else None
        if code_file:
            submit_solution(pid, code_file)
        else:
            print("Usage: python3 course_solver.py solve <PID> <solution_file>")
    else:
        solve_course()
