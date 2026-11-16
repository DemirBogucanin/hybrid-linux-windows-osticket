#!/usr/bin/env python3
import io

import requests

BASE = "http://192.168.31.20/osticket"
r = requests.get(BASE + "/", timeout=20)
lines = r.text.splitlines()
for i in range(40, 70):
    if i < len(lines):
        print(i, lines[i].strip()[:220])
print("--- icon bytes")
for name in ("home.png", "new.png", "status.png"):
    u = f"{BASE}/assets/default/images/icons/{name}"
    b = requests.get(u, timeout=10).content
    print(name, len(b), b[:16])
    try:
        from PIL import Image

        im = Image.open(io.BytesIO(b))
        print("   PIL:", im.size, im.mode)
    except Exception as exc:
        print("   PIL error:", exc)
