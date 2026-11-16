#!/bin/bash
set -u
export LDAPTLS_REQCERT=never

echo '--- bind tdelic@demo.lab'
ldapwhoami -H ldap://192.168.31.10 -ZZ -D 'tdelic@demo.lab' -w 'TDelic2026!' 2>&1
echo "rc=$?"

echo '--- group members via LDAP'
ldapsearch -x -H ldap://192.168.31.10 -ZZ -D 'Administrator@demo.lab' -w "${ADMIN_PW:?set ADMIN_PW}" \
  -b 'CN=osticket-agents,OU=IT_Sektor,DC=demo,DC=lab' '(objectClass=*)' \
  cn sAMAccountName member 2>&1 | grep -E '^(dn:|cn:|sAMAccountName:|member:)'

echo '--- tdelic attributes'
ldapsearch -x -H ldap://192.168.31.10 -ZZ -D 'Administrator@demo.lab' -w "${ADMIN_PW:?set ADMIN_PW}" \
  -b 'DC=demo,DC=lab' '(sAMAccountName=tdelic)' \
  displayName mail sAMAccountName memberOf userAccountControl 2>&1 | grep -E '^(dn:|displayName:|mail:|sAMAccountName:|memberOf:|userAccountControl:)'
