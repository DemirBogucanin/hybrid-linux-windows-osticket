#!/usr/bin/env python3
import re
from urllib.parse import urljoin

import requests

BASE = "http://192.168.31.20/osticket/"
s = requests.Session()
for css in [
    "assets/default/css/theme.css",
    "css/osticket.css",
    "css/font-awesome.min.css",
]:
    url = urljoin(BASE, css)
    r = s.get(url, timeout=20)
    print(f"--- {css} {r.status_code} {len(r.text)}")
    urls = sorted(set(re.findall(r"url\(['\"]?([^'\")]+)", r.text)))
    for u in urls:
        if u.startswith("data:"):
            continue
        full = urljoin(url, u)
        try:
            h = s.head(full, timeout=10, allow_redirects=True)
            if h.status_code != 200:
                print(h.status_code, u, "->", full)
        except Exception as e:
            print("ERR", u, e)
