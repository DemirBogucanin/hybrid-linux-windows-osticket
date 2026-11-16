#!/bin/bash
set -u
export LDAPTLS_REQCERT=never
BIND='CN=svc-osticket,CN=Users,DC=demo,DC=lab'
PW="${LDAP_BIND_PW:?set LDAP_BIND_PW}"

echo '--- whoami'
ldapwhoami -H ldap://192.168.31.10 -ZZ -D "$BIND" -w "$PW"
echo "rc=$?"

echo '--- users'
ldapsearch -x -H ldap://192.168.31.10 -ZZ -D "$BIND" -w "$PW" \
  -b 'DC=demo,DC=lab' '(&(objectClass=user)(objectCategory=person))' \
  sAMAccountName displayName mail | grep -E '^(dn:|sAMAccountName:|displayName:|mail:)' | head -100

echo '--- groups'
ldapsearch -x -H ldap://192.168.31.10 -ZZ -D "$BIND" -w "$PW" \
  -b 'DC=demo,DC=lab' '(objectClass=group)' cn | grep -E '^(dn:|cn:)' | head -100
