#!/usr/bin/env python3
"""Status: report current page state"""
import json, re
from playwright.sync_api import sync_playwright

def status():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
        
        url = page.url
        body = page.evaluate("()=>document.body.innerText")
        pid_m = re.search(r"ProgramID[:\s-]*(\d+)", body)
        cap_vis = page.locator("#capval").is_visible(timeout=300)
        proc_vis = page.locator("#proceedbtn").is_visible(timeout=300)
        editor = page.evaluate("()=>!!document.querySelector('.ace_editor')")
        logged_out = "Sign-in" in body or "Login" in body
        
        data = {
            "url": url[:100],
            "pid": pid_m[1] if pid_m else None,
            "captcha": cap_vis,
            "proceed": proc_vis,
            "editor": editor,
            "logged_out": logged_out,
            "on_course": "codeprogramgroup" in url,
            "on_tutor": "tutorprogram" in url,
        }
        print(json.dumps(data))
        browser.close()

if __name__ == "__main__":
    status()
