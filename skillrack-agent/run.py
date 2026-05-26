#!/usr/bin/env python3
"""Run: pastes code, clicks Run, returns result"""
import sys, time, json
from playwright.sync_api import sync_playwright

def run_code(code, lang="7"):
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
        
        # Set language
        page.evaluate("""(v)=>{
            const s=document.querySelector('#langs_input');
            if(s){s.value=v;s.dispatchEvent(new Event('change'));}
        }""", lang)
        time.sleep(0.3)
        
        # Paste code
        page.evaluate("""(c)=>{
            const ta=document.getElementById('txtCode');
            if(ta) ta.value=c;
            const ed=window.ace.edit(document.querySelector('.ace_editor').id);
            if(ed) ed.getSession().setValue(c);
            if(ta) ta.dispatchEvent(new Event('change',{bubbles:true}));
        }""", code)
        time.sleep(0.5)
        
        # Click Run
        btn = page.locator("button:has-text('Run')")
        if not btn.is_visible(timeout=3000):
            sv = page.locator("button:has-text('Save')")
            if sv.is_visible(timeout=1000): sv.click(); time.sleep(2)
        print("CLICK_RUN")
        btn.click()
        time.sleep(4)
        
        # Wait for result
        for _ in range(45):
            txt = page.evaluate("()=>document.body.innerText").lower()
            if any(x in txt for x in ("passed","failed","error","compilation","time limit")):
                break
            if "please wait" not in txt:
                pass  # Keep waiting
            time.sleep(1)
        
        # Extra wait if still showing "please wait"
        for _ in range(10):
            txt = page.evaluate("()=>document.body.innerText").lower()
            if "please wait" not in txt:
                break
            time.sleep(1)
        
        result = page.evaluate("()=>document.body.innerText")
        pl = result.lower()
        
        data = {
            "passed": ("passed all" in pl or "test case passed" in pl or "all test case" in pl
                       or "your code has passed" in pl or "congratulations" in pl or "code has passed" in pl
                       or "great!" in pl),
            "text": result[:2000]
        }
        print(json.dumps(data))
        browser.close()

def click_proceed():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        btn = page.locator("#proceedbtn")
        if btn.is_visible(timeout=2000):
            btn.click(); time.sleep(4)
            print("PROCEED_CLICKED")
        else:
            print("NO_PROCEED")
        browser.close()

def wait_editor():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        for _ in range(20):
            if page.evaluate("()=>!!document.querySelector('.ace_editor')"):
                print("EDITOR_READY")
                browser.close()
                return
            time.sleep(1)
        print("NO_EDITOR")
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "proceed":
            click_proceed()
        elif sys.argv[1] == "editor":
            wait_editor()
        else:
            # Code passed as string argument
            code = sys.argv[1]
            run_code(code)
    else:
        code = sys.stdin.read()
        run_code(code)
