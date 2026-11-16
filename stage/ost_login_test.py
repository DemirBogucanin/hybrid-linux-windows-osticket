#!/usr/bin/env python3
"""Try an osTicket staff login and report the result."""
import re
import sys

import requests

BASE = "http://192.168.31.20/osticket"
user = sys.argv[1]
password = sys.argv[2]

s = requests.Session()
r = s.get(f"{BASE}/scp/login.php", timeout=20)
m = re.search(r'name="__CSRFToken__" value="([^"]+)"', r.text)
if not m:
    sys.exit("CSRF token not found")
token = m.group(1)
r = s.post(
    f"{BASE}/scp/login.php",
    data={"__CSRFToken__": token, "do": "scplogin", "userid": user, "passwd": password},
    timeout=20,
    allow_redirects=True,
)
print("status:", r.status_code)
print("url:", r.url)
title = re.search(r"<title>(.*?)</title>", r.text, re.S)
print("title:", title.group(1).strip() if title else "(none)")
for pat in ("Invalid", "incorrect", "denied", "Dashboard", "Tickets", "logout"):
    if re.search(pat, r.text, re.I):
        print("contains:", pat)
if "scp/index.php" in r.url or "Dashboard" in r.text:
    s.cookies.save = None
    with open("ost_cookies.txt", "w") as f:
        for c in s.cookies:
            f.write(f"{c.name}\t{c.value}\t{c.domain}\t{c.path}\n")
    print("cookies saved")
