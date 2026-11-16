#!/usr/bin/env python3
"""Small SSH/SFTP helper for the Ubuntu lab VM.

Usage:
  set VM_PASS=...
  python vm.py exec "command"
  python vm.py sudo "command"        # runs via sudo -S bash -c
  python vm.py put  local remote
  python vm.py get  remote local
"""
import os
import shlex
import sys

import paramiko

HOST = "192.168.31.20"
USER = "demir"
PASSWORD = os.environ.get("VM_PASS")

if not PASSWORD:
    sys.exit("VM_PASS environment variable is not set")


def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        HOST,
        username=USER,
        password=PASSWORD,
        timeout=15,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def run(client, command, sudo=False, timeout=600):
    if sudo:
        command = "sudo -S -p '' bash -c " + shlex.quote(command)
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    if sudo:
        stdin.write(PASSWORD + "\n")
        stdin.flush()
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    code = stdout.channel.recv_exit_status()
    if out:
        print(out, end="")
    if err:
        print("STDERR:", err, file=sys.stderr, end="")
    return code


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    action = sys.argv[1]
    client = connect()
    try:
        if action == "exec":
            return run(client, sys.argv[2])
        if action == "sudo":
            return run(client, sys.argv[2], sudo=True)
        if action == "put":
            sftp = client.open_sftp()
            sftp.put(sys.argv[2], sys.argv[3])
            sftp.close()
            print(f"uploaded {sys.argv[2]} -> {sys.argv[3]}")
            return 0
        if action == "get":
            sftp = client.open_sftp()
            sftp.get(sys.argv[2], sys.argv[3])
            sftp.close()
            print(f"downloaded {sys.argv[2]} -> {sys.argv[3]}")
            return 0
        sys.exit(f"unknown action: {action}")
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
