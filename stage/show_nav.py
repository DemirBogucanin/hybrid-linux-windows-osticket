#!/usr/bin/env python3
import requests

r = requests.get("http://192.168.31.20/osticket/", timeout=20)
lines = r.text.splitlines()
for i, line in enumerate(lines):
    if any(k in line for k in ("Support Center Home", "Open a New Ticket", "Check Ticket Status", "powered by", "logo")):
        print(f"{i}: {line.strip()[:400]}")
