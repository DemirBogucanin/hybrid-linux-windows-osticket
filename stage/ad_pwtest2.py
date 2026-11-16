#!/usr/bin/env python3
"""Figure out why AD refuses unicodePwd updates from this host."""
import os
import ssl

from ldap3 import MODIFY_REPLACE, Connection, Server, Tls


def server():
    tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT)
    return Server("192.168.31.10", port=636, use_ssl=True, tls=tls, get_info="ALL")


def admin():
    return Connection(server(), user="Administrator@demo.lab", password=os.environ.get("ADMIN_PW", "CHANGE_ME"), auto_bind=True)


c = admin()
print("socket:", type(c.socket).__name__)
print("rootDSE isReadOnly:", c.server.info.other.get("isReadOnly"))
print("rootDSE dnsHostName:", c.server.info.other.get("dnsHostName"))
print("rootDSE supportedLDAPVersion:", c.server.info.other.get("supportedLDAPVersion"))

for dn in (
    "CN=Tarik Delic,OU=IT_Sektor,DC=demo,DC=lab",
    "CN=Haris Sokolovic,OU=IT_Sektor,DC=demo,DC=lab",
):
    pw = "Str0ng!Lab#2026xyz"
    ok = c.modify(dn, {"unicodePwd": [(MODIFY_REPLACE, [f'"{pw}"'])]})
    print(dn, "->", ok, c.result.get("description"), c.result.get("message"))
    if ok:
        c.modify(dn, {"pwdLastSet": [(MODIFY_REPLACE, ["-1"])]})
        tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT)
        srv = Server("192.168.31.10", port=636, use_ssl=True, tls=tls, get_info="NONE")
        t = Connection(srv, user="tdelic@demo.lab" if "Tarik" in dn else "hsokolovic@demo.lab",
                       password=pw, auto_bind=False, raise_exceptions=False)
        bound = t.bind()
        print("   test bind:", bound, t.result.get("description"))
        t.unbind()
