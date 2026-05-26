#!/usr/bin/env python3
"""CAPTCHA solver: finds and solves captcha on current page"""
import sys, re, base64, io, subprocess, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageOps, ImageFilter

def solve():
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        
        inp = page.locator("#capval")
        if not inp.is_visible(timeout=800):
            print("NO_CAPTCHA")
            browser.close()
            return
        
        b64 = page.evaluate("""()=>{for(const i of document.querySelectorAll('img'))
            if(i.src&&i.src.includes('base64')&&i.offsetParent!==null)return i.src;return null;}""")
        if not b64:
            print("NO_IMG")
            browser.close()
            return
        
        raw = base64.b64decode(b64.split(",")[1].rstrip("=")+"==")
        img = Image.open(io.BytesIO(raw)).convert("L")
        img = ImageOps.autocontrast(img,cutoff=2)
        img = img.resize((img.width*4,img.height*4),Image.LANCZOS)
        img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
        img = ImageOps.invert(img)
        img.save("/tmp/sr_cap.png")
        
        ans = None
        for psm in ["6","8","7"]:
            subprocess.run(["tesseract","/tmp/sr_cap.png","/tmp/sr_o",
                           "--psm",psm,"--oem","3","-c","tessedit_char_whitelist=0123456789+*"],
                          capture_output=True,timeout=10)
            lines=[l.strip() for l in open("/tmp/sr_o.txt").read().split("\n") if l.strip()]
            txt_ocr = lines[-1] if lines else ""
            cm={"O":"0","S":"5","s":"5","l":"1","I":"1","B":"8","b":"6","g":"9","q":"9","T":"7","Z":"2","z":"2"}
            for k,v in cm.items(): txt_ocr = txt_ocr.replace(k,v)
            txt_ocr = re.sub(r"[^0-9+]","",txt_ocr)
            if "+" in txt_ocr:
                p = txt_ocr.split("+")
                l = re.findall(r"\d+",p[0]); r = re.findall(r"\d+",p[1])
                a = next((int(d) for d in reversed(l) if len(d)<=3),None)
                b = next((int(d) for d in r if len(d)<=3),None)
                if a is not None and b is not None: ans=a+b; break
        
        if ans is not None and 0<=ans<=999:
            inp.fill(str(ans))
            print(f"OK {ans}")
        else:
            print("FAIL")
        
        browser.close()

if __name__ == "__main__":
    solve()
