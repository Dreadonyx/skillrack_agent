#!/usr/bin/env python3
"""Read problem: gets PID, title, description, and template code"""
import sys, json
from playwright.sync_api import sync_playwright

def read():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
        
        body = page.evaluate("()=>document.body.innerText")
        import re
        pid_m = re.search(r"ProgramID[:\s-]*(\d+)", body)
        pid = pid_m[1] if pid_m else "???"
        title = "???"
        for i, l in enumerate(body.split("\n")):
            if "ProgramID" in l and i+1 < len(body.split("\n")):
                title = body.split("\n")[i+1].strip()[:80]
                break
        
        # Get template from editor if available
        template = ""
        if page.evaluate("()=>!!document.querySelector('.ace_editor')"):
            template = page.evaluate("""()=>{
                const ed=window.ace.edit(document.querySelector('.ace_editor').id);
                return ed?ed.getSession().getValue():'';
            }""")
        
        data = {"pid": pid, "title": title, "body": body[:3000], "template": template}
        print(json.dumps(data))
        browser.close()

if __name__ == "__main__":
    read()
