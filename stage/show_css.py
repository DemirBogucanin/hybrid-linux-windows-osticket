#!/usr/bin/env python3
import re

import requests

css = requests.get("http://192.168.31.20/osticket/assets/default/css/theme.css", timeout=20).text
for pat in (".home", ".new", ".status", "poweredBy", "#logo", "background"):
    print("===", pat)
    for m in re.finditer(r"[^{}]*" + re.escape(pat) + r"[^{}]*\{[^}]*\}", css):
        block = m.group(0).strip()
        if len(block) < 600:
            print(block)
            print()
