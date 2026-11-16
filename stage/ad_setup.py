#!/usr/bin/env python3
"""Prepare demo.lab for the osTicket LDAP integration.

Run from the Windows workstation (LDAPS 636 to the DC is reachable):

  * create the global security group `osticket-agents` in OU=IT_Sektor
  * add the IT agents (`tdelic`, `hsokolovic`) to it
  * give `tdelic` a known password and make sure the account is usable

Uses the Domain Administrator account supplied by the user.
"""
import os
import ssl
import sys

from ldap3 import MODIFY_ADD, MODIFY_REPLACE, Connection, Server, Tls
from ldap3.core.exceptions import LDAPException
from ldap3.extend.microsoft.modifyPassword import ad_modify_password

DC_HOST = "192.168.31.10"
ADMIN_USER = "Administrator@demo.lab"
ADMIN_PW = os.environ.get("ADMIN_PW", "CHANGE_ME")
BASE = "DC=demo,DC=lab"
OU = "OU=IT_Sektor," + BASE
GROUP_CN = "osticket-agents"
GROUP_DN = f"CN={GROUP_CN},{OU}"
MEMBERS = ["tdelic", "hsokolovic"]
RESET_USER = "tdelic"
NEW_PW = "TDelic2026!"


def connect():
    tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS_CLIENT)
    server = Server(DC_HOST, port=636, use_ssl=True, tls=tls, get_info="ALL")
    conn = Connection(server, user=ADMIN_USER, password=ADMIN_PW, auto_bind=True)
    print("bound as", conn.extend.standard.who_am_i())
    return conn


def find_dn(conn, sam):
    conn.search(BASE, f"(sAMAccountName={sam})", attributes=["distinguishedName"])
    if not conn.entries:
        return None
    return conn.entries[0].entry_dn


def ensure_group(conn):
    dn = find_dn(conn, GROUP_CN)
    if dn:
        print("group exists:", dn)
        return dn
    ok = conn.add(
        GROUP_DN,
        ["top", "group"],
        {
            "cn": GROUP_CN,
            "sAMAccountName": GROUP_CN,
            "groupType": -2147483646,  # global security group
            "description": "osTicket agents (demo.lab)",
        },
    )
    print("create group:", ok, conn.result)
    if not ok:
        sys.exit("could not create group")
    return GROUP_DN


def ensure_members(conn, group_dn):
    for sam in MEMBERS:
        user_dn = find_dn(conn, sam)
        if not user_dn:
            print("user missing, skipped:", sam)
            continue
        ok = conn.modify(group_dn, {"member": [(MODIFY_ADD, [user_dn])]})
        if not ok and conn.result.get("result") == 68:  # already a member
            print("member already present:", sam)
            continue
        print("member:", sam, "->", ok, conn.result.get("description"))


def reset_password(conn, sam, password):
    dn = find_dn(conn, sam)
    if not dn:
        sys.exit(f"user {sam} not found")
    try:
        ad_modify_password(conn, dn, password, old_password=None)
        print("password reset ok:", sam)
    except LDAPException as exc:
        print("password reset failed:", exc)
        sys.exit(1)

    # Clear "must change password at next logon" and make sure account is enabled.
    conn.search(dn, "(objectClass=*)", attributes=["userAccountControl", "pwdLastSet"])
    uac = int(conn.entries[0]["userAccountControl"].value or 512)
    if uac & 2:
        uac &= ~2
        conn.modify(dn, {"userAccountControl": [(MODIFY_REPLACE, [uac])]})
        print("account enabled, userAccountControl =", uac)
    for value in ("-1", -1):
        if conn.modify(dn, {"pwdLastSet": [(MODIFY_REPLACE, [value])]}):
            print("pwdLastSet cleared:", value)
            break
    else:
        print("could not clear pwdLastSet:", conn.result)


def verify(conn, group_dn):
    conn.search(
        BASE,
        f"(memberOf={group_dn})",
        attributes=["sAMAccountName", "displayName"],
    )
    print("--- members of", GROUP_CN)
    for e in conn.entries:
        print("  ", e.entry_dn)


def main():
    conn = connect()
    group_dn = ensure_group(conn)
    ensure_members(conn, group_dn)
    reset_password(conn, RESET_USER, NEW_PW)
    verify(conn, group_dn)
    conn.search(
        BASE,
        f"(sAMAccountName={RESET_USER})",
        attributes=["displayName", "sAMAccountName", "userAccountControl", "mail"],
    )
    print("--- test user")
    for e in conn.entries:
        print(e)


if __name__ == "__main__":
    main()
