#!/bin/bash
set -u
F=/var/www/html/osticket/include/plugins/auth-ldap/authentication.php
echo '--- key functions'
grep -n 'function ' "$F" | head -40
echo '--- mail / search filter'
grep -n -E 'mail|sAMAccountName|userPrincipalName|filter|search' "$F" | head -50
