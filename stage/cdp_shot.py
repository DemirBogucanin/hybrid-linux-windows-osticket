#!/usr/bin/env python3
"""Drive a headless Edge/Chrome over CDP to screenshot authenticated pages.

The osTicket admin panel needs a login, so this script logs in through

the normal form, then captures the requested pages to PNG files.
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import requests
import websocket

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
PORT = 9333
BASE = "http://192.168.31.20/osticket"


def find_edge():
    for path in EDGE_CANDIDATES:
        if os.path.exists(path):
            return path
    sys.exit("Edge not found")


class Page:
    def __init__(self, url):
        self.ws = websocket.create_connection(url, timeout=30)
        self.n = 0

    def send(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result", {})

    def navigate(self, url, settle=2.5):
        self.send("Page.navigate", url=url)
        time.sleep(settle)

    def shot(self, path):
        res = self.send(
            "Page.captureScreenshot",
            format="png",
            captureBeyondViewport=False,
        )
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(res["data"]))
        print("saved", path, os.path.getsize(path))


def main():
    profile = tempfile.mkdtemp(prefix="edge-cdp-")
    proc = subprocess.Popen(
        [
            find_edge(),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile}",
            f"--remote-debugging-port={PORT}",
            "--window-size=1440,1000",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        ver = None
        for _ in range(60):
            try:
                ver = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2))
                break
            except Exception:
                time.sleep(0.5)
        if not ver:
            sys.exit("devtools not reachable")

        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?about:blank", method="PUT")
        target = json.load(urllib.request.urlopen(req, timeout=10))

        page = Page(target["webSocketDebuggerUrl"])
        page.send("Page.enable")
        page.send("Network.enable")
        page.send("Emulation.setDeviceMetricsOverride", width=1440, height=1000, deviceScaleFactor=1, mobile=False)

        # Authenticate with osTicket using the normal login form.
        s = requests.Session()
        r = s.get(f"{BASE}/scp/login.php", timeout=20)
        import re

        token = re.search(r'name="__CSRFToken__" value="([^"]+)"', r.text).group(1)
        s.post(
            f"{BASE}/scp/login.php",
            data={"__CSRFToken__": token, "do": "scplogin", "userid": os.environ.get("OST_ADMIN_USER", "ocadmin"),
            "passwd": os.environ.get("OST_ADMIN_PW", "CHANGE_ME")},
            timeout=20,
        )

        for cookie in s.cookies:
            page.send(
                "Network.setCookie",
                name=cookie.name,
                value=cookie.value,
                domain="192.168.31.20",
                path=cookie.path or "/",
                httpOnly=False,
            )

        shots = [
            ("/scp/index.php", "03-admin-dashboard.png"),
            ("/scp/plugins.php?id=1", "04-ldap-plugin.png"),
            ("/scp/plugins.php?id=1&xid=2", "05-ldap-plugin-config.png"),
        ]
        outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "screenshots")
        outdir = os.path.abspath(outdir)
        for path, name in shots:
            page.navigate(BASE + path)
            title = page.send("Runtime.evaluate", expression="document.title")["result"]["value"]
            print(path, "->", title)
            page.shot(os.path.join(outdir, name))

        page.send("Page.close")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except Exception:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
