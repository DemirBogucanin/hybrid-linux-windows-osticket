#!/usr/bin/env python3
import re

import requests

BASE = "http://192.168.31.20/osticket/"
s = requests.Session()
r = s.get(BASE, timeout=20)
print("status:", r.status_code)
srcs = sorted(set(re.findall(r'<img[^>]+src=["\']([^"\']+)', r.text)))
print("--- images")
for src in srcs:
    url = requests.compat.urljoin(BASE, src)
    try:
        h = s.head(url, timeout=10, allow_redirects=True)
        print(h.status_code, src)
    except Exception as e:
        print("ERR", src, e)
print("--- css/js")
for src in sorted(set(re.findall(r'<(?:link|script)[^>]+(?:href|src)=["\']([^"\']+)', r.text))):
    url = requests.compat.urljoin(BASE, src)
    try:
        h = s.head(url, timeout=10, allow_redirects=True)
        print(h.status_code, src)
    except Exception as e:
        print("ERR", src, e)
