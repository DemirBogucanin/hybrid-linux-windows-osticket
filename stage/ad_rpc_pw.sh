#!/bin/bash
set -u
DC=192.168.31.10
ADMIN="Administrator%${ADMIN_PW:?set ADMIN_PW}"
PW="${NEW_PW:?set NEW_PW}"
export LDAPTLS_REQCERT=never

echo '--- rpcclient path'
command -v rpcclient || echo missing

echo '--- samr set password for tdelic'
rpcclient -U "$ADMIN" "$DC" -c "setuserinfo2 tdelic 23 $PW" 2>&1
echo "rc=$?"

echo '--- bind test tdelic'
ldapwhoami -H ldap://$DC -ZZ -D 'tdelic@demo.lab' -w "$PW" 2>&1
echo "rc=$?"

echo '--- account flags'
rpcclient -U "$ADMIN" "$DC" -c "queryuser tdelic" 2>&1 | grep -iE 'Account Flags|Password Last Set|Logon Count|User Name' | head -10
