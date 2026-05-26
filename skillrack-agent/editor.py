"""
Editor module for SkillRack — paste code, set language, run, parse result.
"""
import re

LANG_VALS = {"C":"2","CPP":"3","JAVA":"1","PYTHON3":"7"}

def wait_for_editor(page, timeout=20):
    for i in range(timeout):
        if page.evaluate("() => !!document.querySelector('.ace_editor')"):
            return True
        import time; time.sleep(1)
    return False

def get_template(page):
    return page.evaluate("""() => {
        const editor = window.ace.edit(document.querySelector('.ace_editor').id);
        if (editor) return editor.getSession().getValue();
        return document.getElementById('txtCode')?.value || '';
    }""")

def set_language(page, lang="PYTHON3"):
    v = LANG_VALS.get(lang.upper(), "7")
    page.evaluate("""(v) => {
        const sel = document.querySelector('#langs_input');
        if (sel) { sel.value = v; sel.dispatchEvent(new Event('change')); }
    }""", v)

def paste(page, code):
    print(f"  Pasting code ({len(code)} bytes)...")
    page.evaluate("""(c) => {
        const ta = document.getElementById('txtCode');
        if (ta) ta.value = c;
        const editor = window.ace.edit(document.querySelector('.ace_editor').id);
        if (editor) editor.getSession().setValue(c);
        if (ta) ta.dispatchEvent(new Event('change', {bubbles: true}));
    }""", code)

def run_and_wait(page):
    run = page.locator("button:has-text('Run')")
    if not run.is_visible(timeout=3000):
        save = page.locator("button:has-text('Save')")
        if save.is_visible(timeout=1000):
            print("  Clicking Save first...")
            save.click()
            import time; time.sleep(2)
    print("  Clicking Run...")
    run.click()
    import time; time.sleep(4)
    for _ in range(25):
        text = page.evaluate("() => document.body.innerText")
        bl = text.lower()
        if any(x in bl for x in ("passed all", "test case passed", "all test case",
                                  "did not pass", "compilation error", "runtime error",
                                  "syntax error", "time limit", "error in execution")):
            return text
        import time; time.sleep(1)
    return page.evaluate("() => document.body.innerText")

def parse_result(body):
    b = body.lower()
    if any(x in b for x in ("passed all", "test case passed", "all test case")):
        return {"passed": True, "text": "ALL TEST CASES PASSED"}
    pm = re.search(r"(\d+)\s+passed", body)
    if pm: return {"passed": True, "text": f"{pm[1]} test cases passed"}
    if "did not pass" in b: return {"passed": False, "text": "Test cases failed (wrong output)"}
    if "compilation error" in b or "syntax error" in b: return {"passed": False, "text": "Compilation error"}
    if "runtime error" in b: return {"passed": False, "text": "Runtime error"}
    if "time limit" in b: return {"passed": False, "text": "Time limit exceeded"}
    if "error in execution" in b: return {"passed": False, "text": "Error in execution"}
    tm = re.search(r"(\d+)\s*/\s*(\d+)", body)
    if tm: return {"passed": tm[1]==tm[2], "text": f"{tm[1]}/{tm[2]} test cases passed"}
    return {"passed": False, "text": "Unknown result"}
