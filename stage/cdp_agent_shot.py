#!/usr/bin/env python3
"""Screenshot the agent and client panels after a real AD login."""
import base64
import json
import os
import re
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
PORT = 9334
BASE = "http://192.168.31.20/osticket"
AGENT = (os.environ.get("AGENT_USER", "tdelic"),
         os.environ.get("AGENT_PW", "CHANGE_ME"))
CLIENT = (os.environ.get("CLIENT_USER", "tdelic@demo.lab"),
          os.environ.get("CLIENT_PW", "CHANGE_ME"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "screenshots")


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
        data = self.send("Page.captureScreenshot", format="png")["data"]
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(data))
        print("saved", path, os.path.getsize(path))


def agent_cookies():
    s = requests.Session()
    r = s.get(f"{BASE}/scp/login.php", timeout=20)
    token = re.search(r'name="__CSRFToken__" value="([^"]+)"', r.text).group(1)
    r = s.post(
        f"{BASE}/scp/login.php",
        data={"__CSRFToken__": token, "do": "scplogin", "userid": AGENT[0], "passwd": AGENT[1]},
        timeout=20,
    )
    print("agent login url:", r.url)
    return s.cookies


def client_cookies():
    s = requests.Session()
    r = s.get(f"{BASE}/login.php", timeout=20)
    token = re.search(r'name="__CSRFToken__" value="([^"]+)"', r.text).group(1)
    r = s.post(
        f"{BASE}/login.php",
        data={"__CSRFToken__": token, "luser": CLIENT[0], "lpasswd": CLIENT[1]},
        timeout=20,
    )
    print("client login url:", r.url)
    return s.cookies


def apply(page, cookies):
    for c in cookies:
        page.send(
            "Network.setCookie",
            name=c.name,
            value=c.value,
            domain="192.168.31.20",
            path=c.path or "/",
        )


def main():
    profile = tempfile.mkdtemp(prefix="edge-cdp2-")
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
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?about:blank", method="PUT")
        target = json.load(urllib.request.urlopen(req, timeout=10))
        page = Page(target["webSocketDebuggerUrl"])
        page.send("Page.enable")
        page.send("Network.enable")
        page.send("Emulation.setDeviceMetricsOverride", width=1440, height=1000, deviceScaleFactor=1, mobile=False)

        apply(page, agent_cookies())
        page.navigate(BASE + "/scp/index.php")
        print("title:", page.send("Runtime.evaluate", expression="document.title")["result"]["value"])
        page.shot(os.path.join(OUT, "06-agent-dashboard-ad.png"))

        page.send("Network.clearBrowserCookies")
        apply(page, client_cookies())
        page.navigate(BASE + "/tickets.php")
        print("title:", page.send("Runtime.evaluate", expression="document.title")["result"]["value"])
        page.shot(os.path.join(OUT, "07-client-portal-ad.png"))

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
