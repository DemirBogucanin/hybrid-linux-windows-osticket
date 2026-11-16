#!/usr/bin/env python3
"""Try the osTicket client (end-user) login with an AD account."""
import os
import re
import sys

import requests

BASE = "http://192.168.31.20/osticket"
user = sys.argv[1] if len(sys.argv) > 1 else "tdelic@demo.lab"
password = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("CLIENT_PW", "CHANGE_ME")

s = requests.Session()
r = s.get(f"{BASE}/login.php", timeout=20)
token = re.search(r'name="__CSRFToken__" value="([^"]+)"', r.text).group(1)
r = s.post(
    f"{BASE}/login.php",
    data={"__CSRFToken__": token, "luser": user, "lpasswd": password},
    timeout=20,
    allow_redirects=True,
)
print("status:", r.status_code)
print("url:", r.url)
title = re.search(r"<title>(.*?)</title>", r.text, re.S)
print("title:", title.group(1).strip() if title else "(none)")
for pat in ("Invalid", "incorrect", "denied", "My Tickets", "Open a New Ticket", "Log Out", "Logout"):
    if re.search(pat, r.text, re.I):
        print("contains:", pat)
