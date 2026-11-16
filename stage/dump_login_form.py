#!/usr/bin/env python3
import re

import requests

r = requests.get("http://192.168.31.20/osticket/login.php", timeout=20)
print("status:", r.status_code)
for m in re.finditer(r"<form[^>]*>", r.text):
    print("FORM:", m.group(0))
for m in re.finditer(r"<input[^>]*>", r.text):
    print("INPUT:", m.group(0).strip()[:200])
for m in re.finditer(r"<select[^>]*>", r.text):
    print("SELECT:", m.group(0))
