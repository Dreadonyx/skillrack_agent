#!/usr/bin/env python3
"""Navigation: go to programming → level1 → codetutor → python → course"""
import sys, time
from playwright.sync_api import sync_playwright

def run(args):
    target = args[0] if args else "course"
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
        
        if target == "course":
            page.goto("https://skillrack.com/faces/candidate/trackshome.xhtml",
                      wait_until="domcontentloaded",timeout=15000); time.sleep(2)
            page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
            for _ in range(8):
                for btn in page.locator("button:has-text('View'),a:has-text('View')").all():
                    p = btn.evaluate("el=>(el.closest('div,tr,td,li')||el).innerText")
                    if "Level 1" in p or "LEVEL" in p:
                        btn.click(); time.sleep(2); break
                else: time.sleep(0.5); continue
                break
            for _ in range(10):
                for btn in page.locator("button:has-text('View'),a:has-text('View')").all():
                    p = btn.evaluate("el=>(el.closest('div,tr,td,li')||el).innerText")
                    if "Learn C" in p or ("Java" in p and "Python" not in p and "JavaScript" not in p):
                        btn.click(); time.sleep(2); break
                else: time.sleep(0.5); continue
                break
            if "CODETUTOR" not in page.url:
                page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                          wait_until="domcontentloaded",timeout=15000); time.sleep(2)
            page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
            page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click(); time.sleep(1.5)
            page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click(); time.sleep(1.5)
            print("COURSE_READY")
            print(f"URL: {page.url}")
        
        elif target.isdigit():
            # Open specific chapter by index
            idx = int(target)
            page.locator(f"#j_id_4i\\:cttbl\\:{idx}\\:j_id_4q").click(); time.sleep(4)
            print(f"CHAPTER_OPENED {idx}")
        
        elif target == "back":
            # Go back to course page
            page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                      wait_until="domcontentloaded",timeout=15000); time.sleep(2)
            page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
            page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click(); time.sleep(1.5)
            page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click(); time.sleep(1.5)
            print("COURSE_READY")
        
        browser.close()

if __name__ == "__main__":
    run(sys.argv[1:])
