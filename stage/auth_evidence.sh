#!/bin/bash
set -u
export LDAPTLS_REQCERT=never
ADMIN='Administrator@demo.lab'
PW="${ADMIN_PW:?set ADMIN_PW}"

echo '--- tdelic logon timestamps'
ldapsearch -x -H ldap://192.168.31.10 -ZZ -D "$ADMIN" -w "$PW" \
  -b 'DC=demo,DC=lab' '(sAMAccountName=tdelic)' \
  lastLogonTimestamp lastLogon logonCount badPwdCount pwdLastSet 2>&1 \
  | grep -E '^(dn:|lastLogon|logonCount|badPwdCount|pwdLastSet)'

echo '--- recent osticket auth syslog'
mysql -u osticket -p"${OST_DB_PW:?set OST_DB_PW}" osticket -e \
  "select log_id, created, title, log_type, LEFT(clean_log,160) msg from ost_syslog order by log_id desc limit 12;" 2>&1 | head -30
