#!/usr/bin/env python3
import requests

for u in [
    "assets/default/images/icons/home.png",
    "assets/default/images/icons/new.png",
    "assets/default/images/icons/status.png",
    "assets/default/images/poweredby.png",
    "assets/default/css/theme.css",
]:
    url = "http://192.168.31.20/osticket/" + u
    r = requests.get(url, timeout=10)
    print(u, r.status_code, r.headers.get("Content-Type"), len(r.content), r.content[:8])
