#!/bin/bash
set -u
export LDAPTLS_REQCERT=never
BIND='CN=svc-osticket,CN=Users,DC=demo,DC=lab'
PW="${LDAP_BIND_PW:?set LDAP_BIND_PW}"

echo '--- bind as demir@demo.lab'
ldapwhoami -H ldap://192.168.31.10 -ZZ -D "demir@demo.lab" -w "${TEST_USER_PW:?set TEST_USER_PW}" 2>&1
echo "rc=$?"

echo '--- osticket groups'
ldapsearch -x -H ldap://192.168.31.10 -ZZ -D "$BIND" -w "$PW" \
  -b 'DC=demo,DC=lab' '(&(objectClass=group)(|(cn=*osticket*)(cn=*agent*)))' cn member 2>&1 | head -60

echo '--- tdelic memberOf'
ldapsearch -x -H ldap://192.168.31.10 -ZZ -D "$BIND" -w "$PW" \
  -b 'DC=demo,DC=lab' '(sAMAccountName=tdelic)' sAMAccountName memberOf 2>&1 | head -30
