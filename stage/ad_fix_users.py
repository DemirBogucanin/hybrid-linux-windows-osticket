#!/usr/bin/env python3
"""Fill in the missing `mail` and `displayName` attributes on demo.lab users.

The LDAP plugin resolves `user@domain` logins through the `mail` attribute, so
without it client (and email-based agent) login fails even though the password
is correct.
"""
import os
import ssl

from ldap3 import MODIFY_ADD, Connection, Server, Tls

DC = "192.168.31.10"
BASE = "DC=demo,DC=lab"
USERS = {
    "ahadzic": "Amar Hadzic",
    "lkovacevic": "Lejla Kovacevic",
    "tdelic": "Tarik Delic",
    "smehmedovic": "Selma Mehmedovic",
    "hsokolovic": "Haris Sokolovic",
    "nimamovic": "Nejra Imamovic",
}


def conn():
    tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT)
    return Connection(
        Server(DC, port=636, use_ssl=True, tls=tls, get_info="ALL"),
        user="Administrator@demo.lab",
        password=os.environ.get("ADMIN_PW", "CHANGE_ME"),
        auto_bind=True,
    )


c = conn()
for sam, name in USERS.items():
    found = c.search(BASE, f"(sAMAccountName={sam})", attributes=["displayName", "mail", "cn"])
    if not found or not c.entries:
        print(sam, "-> not found")
        continue
    e = c.entries[0]
    dn = e.entry_dn
    changes = {}
    if not e["mail"].value:
        changes["mail"] = [(MODIFY_ADD, [f"{sam}@demo.lab"])]
    if not e["displayName"].value:
        changes["displayName"] = [(MODIFY_ADD, [name])]
    if not changes:
        print(sam, "-> already complete (mail:", e["mail"].value, ")")
        continue
    ok = c.modify(dn, changes)
    print(sam, "->", ok, c.result.get("description"), list(changes))

print("--- verify")
for sam in USERS:
    c.search(BASE, f"(sAMAccountName={sam})", attributes=["displayName", "mail"])
    e = c.entries[0]
    print(f"{sam}: mail={e['mail'].value!r} displayName={e['displayName'].value!r}")
