#!/bin/bash
set -u
export LDAPTLS_REQCERT=never

echo '--- bind Administrator@demo.lab (StartTLS)'
ldapwhoami -H ldap://192.168.31.10 -ZZ -D 'Administrator@demo.lab' -w "${ADMIN_PW:?set ADMIN_PW}" 2>&1
echo "rc=$?"

echo '--- bind Administrator@demo.lab (plain, for reference)'
ldapwhoami -H ldap://192.168.31.10 -D 'Administrator@demo.lab' -w "${ADMIN_PW:?set ADMIN_PW}" 2>&1
echo "rc=$?"

echo '--- port checks'
for p in 636 5985 3389; do
  if timeout 3 bash -c "exec 3<>/dev/tcp/192.168.31.10/$p" 2>/dev/null; then
    echo "port $p open"
  else
    echo "port $p closed"
  fi
done
