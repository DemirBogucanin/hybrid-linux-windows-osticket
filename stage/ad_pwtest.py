#!/usr/bin/env python3
"""Diagnose the password reset for tdelic."""
import os
import ssl
import time

from ldap3 import MODIFY_REPLACE, Connection, Server, Tls

DC = "192.168.31.10"
ADMIN = ("Administrator@demo.lab", os.environ.get("ADMIN_PW", "CHANGE_ME"))
USER_DN = "CN=Tarik Delic,OU=IT_Sektor,DC=demo,DC=lab"
ATTRS = [
    "sAMAccountName",
    "userAccountControl",
    "pwdLastSet",
    "badPwdCount",
    "lockoutTime",
    "msDS-User-Account-Control-Computed",
    "whenChanged",
]


def admin_conn():
    tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT)
    return Connection(
        Server(DC, port=636, use_ssl=True, tls=tls, get_info="ALL"),
        user=ADMIN[0],
        password=ADMIN[1],
        auto_bind=True,
    )


def show(conn, label):
    conn.search(USER_DN, "(objectClass=*)", attributes=ATTRS)
    e = conn.entries[0]
    print("---", label)
    for a in ATTRS:
        print(f"   {a}: {e[a].value}")


conn = admin_conn()
show(conn, "before")

new_pw = os.environ.get("NEW_PW", "CHANGE_ME")
ok = conn.modify(USER_DN, {"unicodePwd": [(MODIFY_REPLACE, ['"' + new_pw + '"'])]})
print("unicodePwd replace:", ok, conn.result)
show(conn, "after pwd change")

for value in ("-1",):
    ok = conn.modify(USER_DN, {"pwdLastSet": [(MODIFY_REPLACE, [value])]})
    print("pwdLastSet", value, "->", ok, conn.result.get("description"))

time.sleep(1)
show(conn, "after pwdLastSet")

# Try a bind as the user with the new password.
tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT)
srv = Server(DC, port=636, use_ssl=True, tls=tls, get_info="NONE")
for label, password in (("new", new_pw), ("name-based", "TDelic2026!")):
    c = Connection(srv, user="tdelic@demo.lab", password=password, auto_bind=False)
    try:
        c.bind()
        print(f"bind {label}: OK ->", c.extend.standard.who_am_i())
        c.unbind()
    except Exception as exc:
        print(f"bind {label}: FAIL {exc}")
