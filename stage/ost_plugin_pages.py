#!/usr/bin/env python3
"""Log in as the temp osTicket admin and report the plugin admin pages."""
import os
import re
import sys

import requests

BASE = "http://192.168.31.20/osticket"
user = "ocadmin"
password = os.environ.get("OST_ADMIN_PW", "CHANGE_ME")

s = requests.Session()
r = s.get(f"{BASE}/scp/login.php", timeout=20)
token = re.search(r'name="__CSRFToken__" value="([^"]+)"', r.text).group(1)
s.post(
    f"{BASE}/scp/login.php",
    data={"__CSRFToken__": token, "do": "scplogin", "userid": user, "passwd": password},
    timeout=20,
)

for path in ("/scp/plugins.php", "/scp/plugins.php?id=1", "/scp/index.php"):
    r = s.get(BASE + path, timeout=20)
    print("===", path, r.status_code, len(r.text))
    links = sorted(set(re.findall(r'href="([^"]*plugins?[^"]*)"', r.text)))
    for link in links[:40]:
        print("   link:", link)
    for pat in ("LDAP", "AD demo.lab", "Installed", "Active", "Enable"):
        if re.search(pat, r.text):
            print("   contains:", pat)
