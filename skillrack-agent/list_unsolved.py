#!/usr/bin/env python3
"""
SkillRack CodeTutor — Python Course: list all problems, identify unsolved ones.
Connect to running Chrome/Brave at port 9222.
"""

import sys, time, re
from playwright.sync_api import sync_playwright

PORT = 9222

def sleep(ms):
    time.sleep(ms / 1000)

def log(msg):
    print(f"  {msg}")

def get_page(context):
    for p in context.pages:
        if "skillrack.com" in p.url:
            p.bring_to_front()
            return p
    p = context.pages[0] if context.pages else context.new_page()
    p.bring_to_front()
    return p

def remove_overlays(page):
    page.evaluate("""() => {
        document.querySelectorAll(".ui-widget-overlay, .blockUI, .blockOverlay")
            .forEach(el => el.remove());
    }""")

def setup_course_page(page):
    """Navigate to codeprogramgroup.xhtml and expand Python > Programming Course."""
    page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
              wait_until="domcontentloaded", timeout=20000)
    sleep(3000)
    remove_overlays(page)

    # Click Python Show (index 2)
    py_btn = page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41")
    if not py_btn.is_visible(timeout=5000):
        log("[!] Python Show button not found")
        return False
    py_btn.click()
    sleep(3000)
    remove_overlays(page)

    # Click Programming Course Show (index 0)
    course_btn = page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h")
    if not course_btn.is_visible(timeout=5000):
        log("[!] Programming Course Show button not found")
        return False
    course_btn.click()
    sleep(4000)
    remove_overlays(page)
    return True

def get_chapter_list(page):
    """Return two lists: (currently_learning_chapters, completed_chapters)
    Each chapter is dict: {name, index, table_type, view_btn_id, section}"""
    chapters = []

    # Tab 0: Currently Learning (cttbl)
    for i in range(20):
        btn_id = f"#j_id_4i\\:cttbl\\:{i}\\:j_id_4q"
        btn = page.locator(btn_id)
        if btn.is_visible(timeout=1000):
            parent_text = btn.evaluate("el => (el.closest('div,tr,td,li') || el).innerText")
            # Clean up the chapter name
            name = parent_text.split("Language")[0].strip().split("\n")[0].strip()
            chapters.append({
                "name": name or f"CurrentlyLearning-{i}",
                "index": i,
                "table_type": "cttbl",
                "tab": "Currently Learning",
                "view_btn_id": btn_id,
            })
        else:
            break

    # Tab 1: Completed (completedtbl) — need to switch tab
    completed_header = page.locator("text=Completed").first
    if completed_header.is_visible(timeout=2000):
        completed_header.click()
        sleep(2000)
        remove_overlays(page)

        for i in range(20):
            btn_id = f"#j_id_4i\\:completedtbl\\:{i}\\:j_id_4z"
            btn = page.locator(btn_id)
            if btn.is_visible(timeout=1000):
                parent_text = btn.evaluate("el => (el.closest('div,tr,td,li') || el).innerText")
                name = parent_text.split("Language")[0].strip().split("\n")[0].strip()
                chapters.append({
                    "name": name or f"Completed-{i}",
                    "index": i,
                    "table_type": "completedtbl",
                    "tab": "Completed",
                    "view_btn_id": btn_id,
                })
            else:
                break

        # Switch back to Currently Learning tab
        current_header = page.locator("text=Currently Learning").first
        if current_header.is_visible(timeout=2000):
            current_header.click()
            sleep(1500)
            remove_overlays(page)

    return chapters

def extract_problem_info(page):
    """Extract problem ID and description from the problem page."""
    body = page.evaluate("() => document.body.innerText")

    # Extract PID — look for "ProgramID- XXXXX" pattern
    pid_match = re.search(r"ProgramID\s*[-:]\s*(\d+)", body, re.IGNORECASE)
    pid = pid_match.group(1) if pid_match else ""

    # Extract title — usually right after the chapter name
    title = ""
    lines = body.split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if pid and pid in line and i + 1 < len(lines):
            title = lines[i + 1].strip()
            break
    if not title:
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and line[0].isupper():
                title = line
                break

    return pid, title[:100] if title else ""

def check_problem_status(page):
    """Determine if the current problem is solved, unsolved, or started.
    Returns: 'UNSOLVED', 'SOLVED', or 'STARTED'"""
    # Check for key buttons
    has_proceed = page.locator("#proceedbtn").is_visible(timeout=1000)
    has_view_solved = page.locator("button:has-text('View Solved')").is_visible(timeout=1000)
    has_continue = page.locator("button:has-text('Continue'), button:has-text('Resume')").is_visible(timeout=1000)
    has_solve = page.locator("button:has-text('Solve')").is_visible(timeout=1000)

    if has_proceed or has_solve:
        return "UNSOLVED"
    if has_view_solved:
        return "SOLVED"
    if has_continue:
        return "STARTED"

    # Fallback: check body text for indicators
    body = page.evaluate("() => document.body.innerText").lower()
    if "view solved" in body:
        return "SOLVED"
    if "proceed to solve" in body or "solve" in body:
        return "UNSOLVED"
    return "UNKNOWN"

def main():
    print("=" * 70)
    print("SkillRack CodeTutor — Python Course Problem Scanner")
    print("=" * 70)

    with sync_playwright() as pw:
        print(f"\n[*] Connecting to browser at 127.0.0.1:{PORT}...")
        browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        context = browser.contexts[0]
        page = get_page(context)
        remove_overlays(page)

        # Check logged in
        body_text = page.evaluate("() => document.body.innerText")
        if "Sign-in" in body_text or "Login" in body_text:
            print("[!] You appear to be logged out. Please log into SkillRack first.")
            browser.close()
            sys.exit(1)
        print("[+] Connected and logged in.")

        # Setup: navigate to course page and expand sections
        print("\n[*] Navigating to Python Programming Course...")
        if not setup_course_page(page):
            print("[!] Failed to navigate to course page. Exiting.")
            browser.close()
            sys.exit(1)

        # Get list of all chapters
        print("\n[*] Reading chapter list...")
        chapters = get_chapter_list(page)
        print(f"\n  Found {len(chapters)} chapters total:")
        for c in chapters:
            log(f"  [{c['tab']}] {c['name']}")

        # Now visit each chapter and check its problem
        print("\n" + "=" * 70)
        print("VISITING EACH CHAPTER...")
        print("=" * 70)

        results = []
        for idx, ch in enumerate(chapters):
            print(f"\n[{idx + 1}/{len(chapters)}] {ch['name']} ({ch['tab']})")

            # Navigate to base page first
            if not setup_course_page(page):
                log("  [!] Failed to navigate to course page, skipping")
                results.append({**ch, "pid": "", "title": "", "status": "ERROR"})
                continue

            # Switch to the correct tab if needed
            if ch["tab"] == "Completed":
                comp_tab = page.locator("text=Completed").first
                if comp_tab.is_visible(timeout=2000):
                    comp_tab.click()
                    sleep(2000)
                    remove_overlays(page)

            # Click View on the chapter
            view_btn = page.locator(ch["view_btn_id"])
            if not view_btn.is_visible(timeout=3000):
                log("  [!] Chapter View button not visible")
                results.append({**ch, "pid": "", "title": "", "status": "ERROR"})
                continue

            log("  Clicking View...")
            view_btn.click()
            sleep(4000)
            remove_overlays(page)

            # Extract problem info
            pid, title = extract_problem_info(page)
            status = check_problem_status(page)

            log(f"  PID: {pid or '(none)'} | Status: {status} | Title: {title[:60]}")
            results.append({**ch, "pid": pid, "title": title, "status": status})

        # === Summary ===
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        unsolved = [r for r in results if r["status"] == "UNSOLVED"]
        solved = [r for r in results if r["status"] == "SOLVED"]
        started = [r for r in results if r["status"] == "STARTED"]
        unknown = [r for r in results if r["status"] not in ("UNSOLVED", "SOLVED", "STARTED")]

        print(f"  Total chapters:      {len(results)}")
        print(f"  Total unsolved:      {len(unsolved)}")
        print(f"  Total solved:        {len(solved)}")
        print(f"  Total started:       {len(started)}")
        if unknown:
            print(f"  Unknown status:      {len(unknown)}")

        if unsolved:
            print("\n─── UNSOLVED PROBLEMS ───")
            for r in unsolved:
                pid_str = r["pid"] if r["pid"] else "???"
                print(f"  PID {pid_str:>6}  [{r['tab']:17s}] {r['name'][:40]:40s} — {r['title']}")

        if started:
            print("\n─── STARTED (INCOMPLETE) ───")
            for r in started:
                pid_str = r["pid"] if r["pid"] else "???"
                print(f"  PID {pid_str:>6}  [{r['tab']:17s}] {r['name'][:40]:40s} — {r['title']}")

        if unknown:
            print("\n─── UNKNOWN STATUS ───")
            for r in unknown:
                pid_str = r["pid"] if r["pid"] else "???"
                print(f"  PID {pid_str:>6}  [{r['tab']:17s}] {r['name'][:40]:40s} — {r['title']}")

        if solved:
            print(f"\n  ({len(solved)} problems already solved — hidden for brevity)")

        print("\n" + "=" * 70)
        browser.close()

if __name__ == "__main__":
    main()
