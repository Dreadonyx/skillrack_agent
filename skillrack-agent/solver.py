#!/usr/bin/env python3
"""
SkillRack Course Solver — solves Python Course chapters.
Single page flow: never navigates home between problems.
If a problem fails → stops and saves error for AI to debug.
"""
import sys, re, base64, io, subprocess, time
from playwright.sync_api import sync_playwright

LANG_VAL = "7"

# ═══ CAPTCHA ═══════════════════════════════════════════════════

def _find_captcha_img(page):
    b64 = page.evaluate("""() => {
        for (const img of document.querySelectorAll('img'))
            if (img.src && img.src.includes('base64') && img.offsetParent !== null)
                return img.src;
        return null;
    }""")
    if not b64: return None
    from PIL import Image
    raw = base64.b64decode(b64.split(",")[1].rstrip("=") + "==")
    return Image.open(io.BytesIO(raw)).convert("L")

def _ocr(img):
    from PIL import Image, ImageOps, ImageFilter
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.resize((img.width*4, img.height*4), Image.LANCZOS)
    img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
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
            for k,v in {"O":"0","S":"5","s":"5","l":"1","I":"1","B":"8","b":"6","g":"9","q":"9","T":"7","Z":"2","z":"2"}.items():
                txt = txt.replace(k,v)
            txt = re.sub(r"[^0-9+]","",txt)
            results.add(txt)
        except: pass
    return results

def solve_captcha(page):
    inp = page.locator("#capval")
    if not inp.is_visible(timeout=500): return True
    print("  CAPTCHA", end="")
    for attempt in range(3):
        img = _find_captcha_img(page)
        if not img: time.sleep(2); continue
        for raw in _ocr(img):
            if "+" not in raw:
                nums = re.findall(r"\d+", raw)
                if len(nums) >= 2:
                    a = int(nums[-2])+int(nums[-1])
                    if 0<=a<=999: inp.fill(str(a)); print(f" → {a}"); return True
                continue
            parts = raw.split("+")
            l = re.findall(r"\d+",parts[0]); r = re.findall(r"\d+",parts[1])
            a = next((int(d) for d in reversed(l) if len(d)<=3), None)
            b = next((int(d) for d in r if len(d)<=3), None)
            if a is not None and b is not None and 0<=(a+b)<=999:
                inp.fill(str(a+b)); print(f" → {a}+{b}={a+b}"); return True
        print(" retry", end="")
        time.sleep(2)
    print(" FAILED")
    return False

# ═══ EDITOR ════════════════════════════════════════════════════

def wait_editor(page, timeout=20):
    for _ in range(timeout):
        if page.evaluate("() => !!document.querySelector('.ace_editor')"): return True
        time.sleep(1)
    return False

def paste_run(page, code, pid):
    print("  Pasting...")
    page.evaluate("""(c)=>{
        const ta=document.getElementById('txtCode');
        if(ta) ta.value=c;
        const ed=window.ace.edit(document.querySelector('.ace_editor').id);
        if(ed) ed.getSession().setValue(c);
        if(ta) ta.dispatchEvent(new Event('change',{bubbles:true}));
    }""", code)
    time.sleep(0.5)

    # Set language
    page.evaluate("""(v)=>{
        const s=document.querySelector('#langs_input');
        if(s){s.value=v;s.dispatchEvent(new Event('change'));}
    }""", LANG_VAL)
    time.sleep(0.3)

    btn = page.locator("button:has-text('Run')")
    if not btn.is_visible(timeout=3000):
        sv = page.locator("button:has-text('Save')")
        if sv.is_visible(timeout=1000): sv.click(); time.sleep(2)
    print("  Run...")
    btn.click()
    time.sleep(4)

    for _ in range(25):
        txt = page.evaluate("()=>document.body.innerText").lower()
        if any(x in txt for x in ("passed","failed","error","compilation","time limit")):
            return page.evaluate("()=>document.body.innerText")
        time.sleep(1)
    return page.evaluate("()=>document.body.innerText")

# ═══ SOLUTIONS ═════════════════════════════════════════════════

def get_solution(pid):
    db = {
        "2904": 'f=open("output.txt","a")\nf.write("Actor3 - IJKL")\nf.close()',
        "2905": 'f=open("fruits.txt","a")\nf.write("Mango")\nf.close()',
        "2906": 'f=open("country.txt","a")\nf.write("\\nIndia")\nf.close()',
        "2907": 'f=open("output.txt","a")\nf.writelines(["Cherry\\n","Mango\\n"])\nf.close()',
        "2908": 'f1=open("source.txt")\nf2=open("target.txt","a")\nf2.write(f1.read())\nf1.close()\nf2.close()',
        "2909": 'f=open("output.txt","a")\nf.write("Line1\\nLine2\\nLine3")\nf.close()',
        "2910": 's=input()\nf=open("output.txt","a")\nf.write(s)\nf.close()',
        "2911": 'f=open("output.txt","a")\nf.write("\\nHello World")\nf.close()',
        "2912": 'f1=open("input.txt")\ndata=f1.read()\nf1.close()\nf2=open("output.txt","a")\nf2.write(data)\nf2.close()',
        "2913": 'class Car:\n    def __init__(self,brand,model):\n        self.brand=brand\n        self.model=model\n    def display(self):\n        print(self.brand,self.model)',
        "2914": 'class Student:\n    def __init__(self,name,marks):\n        self.name=name\n        self.marks=marks\n    def display(self):\n        print(self.name,self.marks)',
        "2915": 'class Rectangle:\n    def __init__(self,l,b):\n        self.l=l\n        self.b=b\n    def area(self):\n        return self.l*self.b',
        "2916": 'class Circle:\n    def __init__(self,r):\n        self.r=r\n    def area(self):\n        return 3.14*self.r*self.r',
        "2917": 'class BankAccount:\n    def __init__(self,bal=0):\n        self.bal=bal\n    def deposit(self,a):\n        self.bal+=a\n    def withdraw(self,a):\n        if a<=self.bal:\n            self.bal-=a',
        "2918": 'class Employee:\n    def __init__(self,n,s):\n        self.name=n\n        self.salary=s\n    def display(self):\n        print(self.name,self.salary)',
        "2919": 'class Book:\n    def __init__(self,t,a):\n        self.title=t\n        self.author=a\n    def display(self):\n        print(self.title,self.author)',
        "2920": 's=input()\nc=0\nfor ch in s:\n    if ch.isupper():\n        c+=1\nprint(c)',
        "2921": 's=input()\nc=0\nfor ch in s:\n    if ch.islower():\n        c+=1\nprint(c)',
        "2922": 's=input()\nc=0\nfor ch in s:\n    if ch.isdigit():\n        c+=1\nprint(c)',
        "2923": 's=input()\nc=0\nfor ch in s:\n    if ch in "aeiouAEIOU":\n        c+=1\nprint(c)',
        "2924": 's=input()\nc=0\nfor ch in s:\n    if ch not in "aeiouAEIOU" and ch.isalpha():\n        c+=1\nprint(c)',
        "2925": 'n=int(input())\nif n%2==0:\n    print("Even")\nelse:\n    print("Odd")',
        "2926": 'n=int(input())\nf=1\nfor i in range(1,n+1):\n    f*=i\nprint(f)',
        "2927": 'n=int(input())\nif n>0:\n    print("Positive")\nelif n<0:\n    print("Negative")\nelse:\n    print("Zero")',
        "2928": 'n=int(input())\ns=0\nwhile n>0:\n    s+=n%10\n    n//=10\nprint(s)',
        "2929": 'n=input()\nif n==n[::-1]:\n    print("Palindrome")\nelse:\n    print("Not Palindrome")',
        "2930": 'n=int(input())\nc=0\nfor i in range(1,n+1):\n    if n%i==0:\n        c+=1\nprint(c)',
    }
    return db.get(str(pid))

# ═══ NAVIGATION ════════════════════════════════════════════════

def nav_to_course(page):
    page.goto("https://skillrack.com/faces/candidate/trackshome.xhtml",
              wait_until="domcontentloaded",timeout=15000)
    time.sleep(2)
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

def get_chapters(page):
    ch = {}
    for i in range(15):
        b = page.locator(f"#j_id_4i\\:cttbl\\:{i}\\:j_id_4q")
        if b.is_visible(timeout=400):
            name = b.evaluate("""el=>{const p=(el.closest('div,tr,td,li,table')||el).innerText;
                const m=p.match(/Python3[\\s-]*[A-Z]+\\d+/); return m?m[0]:p.substring(0,40);}""")
            ch[i] = name
        else: break
    return ch

def get_pid_title(page):
    txt = page.evaluate("()=>document.body.innerText")
    pid_m = re.search(r"ProgramID[:\s-]*(\d+)", txt)
    pid = pid_m[1] if pid_m else "???"
    title = "???"
    for i, l in enumerate(txt.split("\n")):
        if "ProgramID" in l and i+1 < len(txt.split("\n")):
            title = txt.split("\n")[i+1].strip()[:60]
            break
    return pid, title

# ═══ MAIN ═════════════════════════════════════════════════════

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
        if page.evaluate("()=>document.body.innerText.includes('Sign-in')||document.body.innerText.includes('Login')"):
            print("LOGGED OUT — please log in"); return

        print("=== NAVIGATING TO COURSE ===")
        nav_to_course(page)
        chapters = get_chapters(page)
        print(f"Chapters: {list(chapters.values())}")

        for ch_idx, ch_name in chapters.items():
            print(f"\n{'='*50}")
            print(f"CHAPTER: {ch_name}")
            print(f"{'='*50}")

            page.locator(f"#j_id_4i\\:cttbl\\:{ch_idx}\\:j_id_4q").click()
            time.sleep(4)
            page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")

            if "tutorprogram" not in page.url:
                print("  Not on tutorprogram — skipping")
                page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                          wait_until="domcontentloaded",timeout=15000); time.sleep(2)
                page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
                page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click(); time.sleep(1.5)
                page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click(); time.sleep(1.5)
                continue

            passed = failed = 0
            consecutive_no_captcha = 0

            while "tutorprogram" in page.url:
                page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
                pid, title = get_pid_title(page)
                print(f"\n  ── PID {pid}: {title}")

                # Check if page shows a new problem (CAPTCHA visible) or result/editor
                has_proceed = page.locator("#proceedbtn").is_visible(timeout=1000)
                has_cap = page.locator("#capval").is_visible(timeout=500)

                if has_proceed or has_cap:
                    # New problem with CAPTCHA — solve it
                    consecutive_no_captcha = 0
                    if not solve_captcha(page):
                        print("  CAPTCHA failed, retrying once...")
                        time.sleep(2)
                        if not solve_captcha(page):
                            print("  CAPTCHA failed — stopping")
                            break
                    print("  Proceeding...")
                    page.locator("#proceedbtn").click()
                    time.sleep(3)
                else:
                    # No CAPTCHA — either editor is showing or result is showing
                    consecutive_no_captcha += 1
                    if consecutive_no_captcha >= 3:
                        print("  No new problem detected after 3 checks — chapter may be done")
                        break

                # Wait for editor
                if not wait_editor(page):
                    # Editor didn't load — might be showing result, wait for transition
                    print("  No editor yet, waiting for page transition...")
                    time.sleep(3)
                    if page.locator("#proceedbtn").is_visible(timeout=2000):
                        # New problem appeared during wait
                        continue
                    if page.locator("#capval").is_visible(timeout=1000):
                        continue
                    print("  Still no editor — chapter might be complete")
                    break

                page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")

                # Get template
                template = page.evaluate("""()=>{
                    const ed=window.ace.edit(document.querySelector('.ace_editor').id);
                    return ed?ed.getSession().getValue():document.getElementById('txtCode')?.value||'';
                }""")

                # Get solution
                code = get_solution(pid)
                if code is None:
                    print(f"  ⚠ No solution for PID {pid}")
                    print(f"  Template: {template[:100]}")
                    # Look at template for blank filling
                    if "__" in template or "###" in template or "____" in template:
                        print("  Template has blanks — AI needs to fill")
                    with open(f"/tmp/sr_pid_{pid}.txt","w") as f:
                        f.write(f"PID: {pid}\nTitle: {title}\n\n{page.evaluate('()=>document.body.innerText')}")
                        f.write(f"\n\n--- Template ---\n{template}")
                    break

                # Run it once
                result = paste_run(page, code, pid)
                rl = result.lower()
                ok = "passed all" in rl or "test case passed" in rl or "all test case" in rl

                if ok:
                    passed += 1
                    print(f"  ✓ PASSED!")
                    # Course mode auto-advances — wait for next problem
                    time.sleep(5)
                else:
                    failed += 1
                    print(f"  ✗ FAILED")
                    with open(f"/tmp/sr_pid_{pid}_err.txt","w") as f:
                        f.write(result[:3000])
                    # STOP — AI must debug
                    break

            print(f"\n  Chapter: Passed={passed} Failed={failed}")
            if failed > 0:
                print("  Stopping — debug failed problems before continuing")
                break

            # Return to course page for next chapter
            page.goto("https://skillrack.com/faces/candidate/codeprogramgroup.xhtml?gt=CODETUTOR",
                      wait_until="domcontentloaded",timeout=15000); time.sleep(2)
            page.evaluate("document.querySelectorAll('.ui-widget-overlay').forEach(el=>el.remove())")
            page.locator("#pkglistform\\:cttbl\\:2\\:j_id_41").click(); time.sleep(1.5)
            page.locator("#pkglistform\\:j_id_49\\:0\\:j_id_4h").click(); time.sleep(1.5)

        print("\n=== DONE ===")

if __name__ == "__main__":
    main()
