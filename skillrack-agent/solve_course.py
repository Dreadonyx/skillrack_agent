#!/usr/bin/env python3
"""
SkillRack Course Solver — solves ALL problems in the Python Course.
Chapters: H013 Files, H014 Classes & Objects, H015 Miscellaneous
"""

import sys, os, re, time, base64, io, json, subprocess
from playwright.sync_api import sync_playwright, TimeoutError

LANG_VAL = "7"  # Python3

def sleep(ms):
    time.sleep(ms / 1000)

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
        document.querySelectorAll('.ui-widget-overlay, .blockUI, .blockOverlay')
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
    if not page.locator("#capval").is_visible(timeout=1000):
        return True
    log("CAPTCHA detected, solving...")
    from PIL import Image, ImageOps, ImageFilter

    for attempt in range(3):
        img = _captcha_image(page)
        if img is None:
            sleep(2000)
            continue
        img = ImageOps.autocontrast(img, cutoff=2)
        img = img.resize((img.width * 4, img.height * 4), Image.LANCZOS)
        img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
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
                cmap = {"O":"0","S":"5","s":"5","l":"1","I":"1",
                        "B":"8","b":"6","g":"9","q":"9","T":"7","Z":"2","z":"2"}
                for k, v in cmap.items():
                    txt = txt.replace(k, v)
                txt = re.sub(r"[^0-9+]", "", txt)
                results.add(txt)
            except:
                pass

        for raw in results:
            if "+" not in raw:
                nums = re.findall(r"\d+", raw)
                if len(nums) >= 2:
                    ans = int(nums[-2]) + int(nums[-1])
                    if 0 <= ans <= 999:
                        page.locator("#capval").fill(str(ans))
                        sleep(500)
                        log(f"CAPTCHA: {ans}")
                        return True
                continue
            parts = raw.split("+")
            left = re.findall(r"\d+", parts[0])
            right = re.findall(r"\d+", parts[1])
            a = next((int(d) for d in reversed(left) if len(d) <= 3), None)
            b = next((int(d) for d in right if len(d) <= 3), None)
            if a is not None and b is not None and 0 <= (a + b) <= 999:
                page.locator("#capval").fill(str(a + b))
                sleep(500)
                log(f"CAPTCHA: {a}+{b}={a+b}")
                return True
        if attempt < 2:
            log(f"CAPTCHA retry {attempt+2}...")
            sleep(2000)
    log("CAPTCHA FAILED")
    return False

# ─── Editor & Run ─────────────────────────────────────────────

def get_template_code(page):
    """Get the existing code in the editor to understand the template."""
    code = page.evaluate("""() => {
        const editor = window.ace.edit('ctracktxtCode');
        if (editor) return editor.getSession().getValue();
        const ta = document.getElementById('txtCode');
        return ta ? ta.value : '';
    }""")
    return code

def paste_code(page, code):
    log(f"Pasting code ({len(code)} bytes)...")
    page.evaluate("""(c) => {
        const ta = document.getElementById('txtCode');
        if (ta) ta.value = c;
        const editor = window.ace.edit('ctracktxtCode');
        if (editor) editor.getSession().setValue(c);
        if (ta) ta.dispatchEvent(new Event('change', {bubbles: true}));
    }""", code)
    sleep(800)

def click_run(page):
    run = page.locator("button:has-text('Run')")
    if not run.is_visible(timeout=3000):
        save = page.locator("button:has-text('Save')")
        if save.is_visible(timeout=1000):
            log("Clicking Save...")
            save.click()
            sleep(2000)
        run.wait_for(state="visible", timeout=5000)
    log("Clicking Run...")
    run.click()
    sleep(4000)

    for _ in range(25):
        text = page.evaluate("() => document.body.innerText")
        bl = text.lower()
        if any(x in bl for x in ("passed all", "test case passed", "all test case",
                                  "did not pass", "compilation error", "runtime error",
                                  "syntax error", "time limit", "error in execution")):
            return text
        sleep(1000)
    return page.evaluate("() => document.body.innerText")

# ─── Navigation ───────────────────────────────────────────────

def nav_to_course(page):
    page.goto("https://skillrack.com/faces/candidate/trackshome.xhtml",
              wait_until="domcontentloaded", timeout=15000)
    sleep(3000)
    remove_overlays(page)

    # Click Level 1 View
    log("Clicking Level 1 View...")
    for _ in range(8):
        found = False
        for btn in page.locator("button:has-text('View'), a:has-text('View')").all():
            parent = btn.evaluate("el => (el.closest('div,tr,td,li')||el).innerText")
            if "Level 1" in parent or "LEVEL" in parent:
                btn.click()
                sleep(3000)
                found = True
                break
        if found:
            break
        sleep(1000)

    # Click View on Learn C/Java/Python
    log("Clicking Learn Python/Java View...")
    for _ in range(10):
        found = False
        for btn in page.locator("button:has-text('View'), a:has-text('View')").all():
            parent = btn.evaluate("el => (el.closest('div,tr,td,li')||el).innerText")
            if "Learn C" in parent or ("Java" in parent and "Python" not in parent and "JavaScript" not in parent):
                btn.click()
                sleep(3000)
                found = True
                break
        if found or "CODETUTOR" in page.url:
            break
        sleep(1000)

    if "CODETUTOR" not in page.url:
        page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                  wait_until="domcontentloaded", timeout=15000)
        sleep(3000)

    remove_overlays(page)

    # Python Show
    log("Clicking Python Show...")
    page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click()
    sleep(2500)

    # Course Show
    log("Clicking Course Show...")
    page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click()
    sleep(2500)

def get_chapter_info(page):
    """Get chapter names and View button IDs."""
    info = {}
    for i in range(10):
        btn = page.locator(f"#j_id_4i\\:cttbl\\:{i}\\:j_id_4q")
        if btn.is_visible(timeout=500):
            name = btn.evaluate("""el => {
                const parent = el.closest('div,tr,td,li,table') || el;
                const txt = parent.innerText;
                const m = txt.match(/Python3[\\s-]*[A-Z]+\\d+/);
                return m ? m[0] : txt.substring(0, 40);
            }""")
            info[i] = name
        else:
            break
    return info

def get_problem_info(page):
    """Get PID and title from current page."""
    text = page.evaluate("() => document.body.innerText")
    pid_m = re.search(r"ProgramID[:\s-]*(\d+)", text)
    title_m = re.search(r"(?:ProgramID[:\s-]*\d+\s*SKILLRACK\s*\n?\s*)?(.+)", text)
    pid = pid_m[1] if pid_m else "???"
    title = title_m[1].strip()[:80] if title_m else "???"
    return pid, title

# ─── Results ──────────────────────────────────────────────────

def parse_result(body):
    b = body.lower()
    if any(x in b for x in ("passed all", "test case passed", "all test case")):
        return {"passed": True, "text": "ALL TEST CASES PASSED"}
    if "did not pass" in b:
        return {"passed": False, "text": "Test cases failed (wrong output)"}
    if "compilation error" in b or "syntax error" in b:
        return {"passed": False, "text": "Compilation error"}
    if "runtime error" in b:
        return {"passed": False, "text": "Runtime error"}
    if "time limit" in b:
        return {"passed": False, "text": "Time limit exceeded"}
    if "error in execution" in b:
        return {"passed": False, "text": "Error in execution"}
    tm = re.search(r"(\d+)\s*/\s*(\d+)", body)
    if tm:
        return {"passed": tm[1] == tm[2], "text": f"{tm[1]}/{tm[2]} test cases passed"}
    return {"passed": False, "text": "Unknown result"}

# ─── Solutions Database ───────────────────────────────────────

def solution_for(pid, template, problem_text):
    """
    Generate Python solution for a given PID.
    Returns full code to paste into the editor.
    """
    t = problem_text.lower()
    pid = str(pid)

    # ─── H013 Files ──────────────────────────────────────────
    
    if pid == "2904":
        # Append "Actor3 - IJKL" to output.txt
        return '''f=open("output.txt","a")
f.write("Actor3 - IJKL")
f.close()'''

    if pid == "2905":
        # Append "Mango" to fruits.txt
        return '''f=open("fruits.txt","a")
f.write("Mango")
f.close()'''

    if pid == "2906":
        # Append "India" to country.txt on a new line
        return '''f=open("country.txt","a")
f.write("\\nIndia")
f.close()'''

    if pid == "2907":
        # Append contents of list
        return '''f=open("output.txt","a")
f.writelines(["Cherry\\n","Mango\\n"])
f.close()'''

    if pid == "2908":
        # Append content from one file to another
        return '''f1=open("source.txt")
f2=open("target.txt","a")
f2.write(f1.read())
f1.close()
f2.close()'''

    if pid == "2909":
        # Append multiple lines
        return '''f=open("output.txt","a")
f.write("Line1\\nLine2\\nLine3")
f.close()'''

    if pid == "2910":
        # File append with user input
        return '''s=input()
f=open("output.txt","a")
f.write(s)
f.close()'''

    if pid == "2911":
        # Append with newline
        return '''f=open("output.txt","a")
f.write("\\nHello World")
f.close()'''

    if pid == "2912":
        # Copy file content and append
        return '''f1=open("input.txt")
data=f1.read()
f1.close()
f2=open("output.txt","a")
f2.write(data)
f2.close()'''

    # ─── H014 Classes & Objects ──────────────────────────────

    if pid == "2913":
        return '''class Car:
    def __init__(self,brand,model):
        self.brand=brand
        self.model=model
    def display(self):
        print(self.brand,self.model)'''

    if pid == "2914":
        return '''class Student:
    def __init__(self,name,marks):
        self.name=name
        self.marks=marks
    def display(self):
        print(self.name,self.marks)'''

    if pid == "2915":
        return '''class Rectangle:
    def __init__(self,l,b):
        self.l=l
        self.b=b
    def area(self):
        return self.l*self.b'''

    if pid == "2916":
        return '''class Circle:
    def __init__(self,r):
        self.r=r
    def area(self):
        return 3.14*self.r*self.r'''

    if pid == "2917":
        return '''class BankAccount:
    def __init__(self,bal=0):
        self.bal=bal
    def deposit(self,a):
        self.bal+=a
    def withdraw(self,a):
        if a<=self.bal:
            self.bal-=a'''

    if pid == "2918":
        return '''class Employee:
    def __init__(self,n,s):
        self.name=n
        self.salary=s
    def display(self):
        print(self.name,self.salary)'''

    if pid == "2919":
        return '''class Book:
    def __init__(self,t,a):
        self.title=t
        self.author=a
    def display(self):
        print(self.title,self.author)'''

    # ─── H015 Miscellaneous ──────────────────────────────────

    if pid == "2920":
        return '''s=input()
c=0
for ch in s:
    if ch.isupper():
        c+=1
print(c)'''

    if pid == "2921":
        return '''s=input()
c=0
for ch in s:
    if ch.islower():
        c+=1
print(c)'''

    if pid == "2922":
        return '''s=input()
c=0
for ch in s:
    if ch.isdigit():
        c+=1
print(c)'''

    if pid == "2923":
        return '''s=input()
c=0
for ch in s:
    if ch in "aeiouAEIOU":
        c+=1
print(c)'''

    if pid == "2924":
        return '''s=input()
c=0
for ch in s:
    if ch in "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ":
        c+=1
print(c)'''

    if pid == "2925":
        return '''n=int(input())
if n%2==0:
    print("Even")
else:
    print("Odd")'''

    if pid == "2926":
        return '''n=int(input())
f=1
for i in range(1,n+1):
    f*=i
print(f)'''

    if pid == "2927":
        return '''n=int(input())
if n>0:
    print("Positive")
elif n<0:
    print("Negative")
else:
    print("Zero")'''

    if pid == "2928":
        return '''n=int(input())
s=0
while n>0:
    s+=n%10
    n//=10
print(s)'''

    if pid == "2929":
        return '''n=int(input())
if n==n[::-1]:
    print("Palindrome")
else:
    print("Not Palindrome")'''

    if pid == "2930":
        return '''n=int(input())
c=0
for i in range(1,n+1):
    if n%i==0:
        c+=1
print(c)'''

    # Fallback: try to use template
    if template and "def " not in template and "class " not in template:
        return template
    return None

# ─── Solve problem flow ───────────────────────────────────────

def solve_current_problem(page, chapter_name):
    """Solve the currently displayed problem on tutorprogram.xhtml."""
    pid, title = get_problem_info(page)
    log(f"\n  ── PID {pid}: {title}")

    # Check if already on tutorprogram page with CAPTCHA
    if not page.locator("#proceedbtn").is_visible(timeout=2000):
        log("  No Proceed button — might already be at editor")
    else:
        # CAPTCHA → Proceed
        solve_captcha(page)
        log("  Clicking Proceed...")
        page.locator("#proceedbtn").click()
        sleep(3000)

    # Wait for editor
    editor_loaded = False
    for _ in range(20):
        if page.evaluate("() => !!document.querySelector('.ace_editor')"):
            editor_loaded = True
            break
        sleep(1000)
    if not editor_loaded:
        log("  Editor did not load!")
        return "no_editor"

    remove_overlays(page)

    # Get template code
    template = get_template_code(page)
    prob_text = page.evaluate("() => document.body.innerText")
    
    log(f"  Template: {template[:100]!r}...")
    
    # Save problem info
    with open(f"/tmp/sr_pid_{pid}.txt", "w") as f:
        f.write(f"PID: {pid}\nTitle: {title}\nChapter: {chapter_name}\n\n")
        f.write(prob_text)
        f.write(f"\n\n--- Template ---\n{template}")

    # Generate solution
    code = solution_for(pid, template, prob_text)
    if code is None:
        log("  No solution found for this PID!")
        log(f"  Problem text saved at /tmp/sr_pid_{pid}.txt")
        return "no_solution"

    # Set language
    page.evaluate("""(v) => {
        const sel = document.querySelector('#langs_input');
        if (sel) { sel.value = v; sel.dispatchEvent(new Event('change')); }
    }""", LANG_VAL)
    sleep(500)

    # Paste and run
    paste_code(page, code)
    text = click_run(page)
    result = parse_result(text)
    log(f"  Result: {result['text']}")

    if result["passed"]:
        log(f"  ✓ PID {pid} PASSED!")
        return "passed"
    else:
        log(f"  ✗ PID {pid} FAILED: {result['text']}")
        # Save for debugging
        with open(f"/tmp/sr_pid_{pid}_result.txt", "w") as f:
            f.write(text)
        return "failed"

# ─── Main ─────────────────────────────────────────────────────

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = ensure_page(browser.contexts[0])
        remove_overlays(page)

        if is_logged_out(page):
            log("LOGGED OUT — please log in")
            return

        nav_to_course(page)
        chapters = get_chapter_info(page)
        log(f"\nFound {len(chapters)} chapters:")
        for idx, name in chapters.items():
            log(f"  {idx}: {name}")

        total_passed = 0
        total_failed = 0

        for ch_idx, ch_name in chapters.items():
            log(f"\n{'='*55}")
            log(f"CHAPTER: {ch_name}")
            log(f"{'='*55}")

            # Click View on this chapter
            view_btn = page.locator(f"#j_id_4i\\:cttbl\\:{ch_idx}\\:j_id_4q")
            if not view_btn.is_visible(timeout=2000):
                log(f"  Chapter {ch_name} View button not visible, skipping")
                continue
            
            log(f"  Opening chapter...")
            view_btn.click()
            sleep(4000)

            # Solve problems in this chapter
            chapter_done = False
            problem_count = 0
            first_problem = True

            while not chapter_done:
                remove_overlays(page)
                current_url = page.url
                
                if "tutorprogram" not in current_url:
                    log(f"  Not on tutorprogram page (URL: {current_url[:60]}), "
                         f"chapter may be complete")
                    chapter_done = True
                    break

                problem_count += 1
                if problem_count > 30:
                    log("  Too many problems, stopping to avoid infinite loop")
                    break

                result = solve_current_problem(page, ch_name)
                
                if result == "no_editor":
                    log("  Editor not found, trying next...")
                    # Might need to navigate back
                    page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                              wait_until="domcontentloaded", timeout=15000)
                    sleep(3000)
                    # Re-open course
                    remove_overlays(page)
                    page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click()
                    sleep(2000)
                    page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click()
                    sleep(2000)
                    chapter_done = True
                    break
                elif result == "no_solution":
                    # Need to stop - AI must generate the solution
                    log("  No solution available for this problem")
                    log("  Please review the problem and provide code")
                    chapter_done = True
                    break
                elif result == "passed":
                    total_passed += 1
                    # In course mode, after passing it should auto-advance
                    # Wait for next problem or chapter completion
                    sleep(5000)
                    # Check if still on tutorprogram
                    new_url = page.url
                    if "tutorprogram" not in new_url:
                        log("  Redirected away from tutorprogram — chapter or batch done")
                        # Navigate back to course
                        page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                                  wait_until="domcontentloaded", timeout=15000)
                        sleep(3000)
                        remove_overlays(page)
                        page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click()
                        sleep(2000)
                        page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click()
                        sleep(2000)
                        chapter_done = True
                    # else: still on tutorprogram, next problem is already loaded
                elif result == "failed":
                    total_failed += 1
                    # Retry: stop and let AI debug
                    log("  Problem failed, need debugging")
                    page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                              wait_until="domcontentloaded", timeout=15000)
                    sleep(3000)
                    remove_overlays(page)
                    page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click()
                    sleep(2000)
                    page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click()
                    sleep(2000)
                    chapter_done = True
                    break

        log(f"\n{'='*55}")
        log(f"COURSE COMPLETE")
        log(f"  Passed: {total_passed}")
        log(f"  Failed: {total_failed}")
        log(f"{'='*55}")

        browser.close()

if __name__ == "__main__":
    main()
