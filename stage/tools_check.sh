#!/bin/bash
for b in rpcclient smbclient net smbpasswd samba-tool; do
  if command -v "$b" >/dev/null 2>&1; then
    echo "$b: $(command -v "$b")"
  else
    echo "$b: missing"
  fi
done
