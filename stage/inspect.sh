#!/bin/bash
set -u
CONF=/var/www/html/osticket/include/ost-config.php
echo '--- config'
grep -E 'DBHOST|DBNAME|DBUSER|DBPASS|TABLE_PREFIX|SECRET_SALT' "$CONF"
DBPASS=$(grep -oP "define\('DBPASS',\s*'[^']*'" "$CONF" | sed "s/.*'\([^']*\)'$/\1/")
DBNAME=$(grep -oP "define\('DBNAME',\s*'[^']*'" "$CONF" | sed "s/.*'\([^']*\)'$/\1/")
DBUSER=$(grep -oP "define\('DBUSER',\s*'[^']*'" "$CONF" | sed "s/.*'\([^']*\)'$/\1/")
echo "--- tables in $DBNAME"
mysql -u "$DBUSER" -p"$DBPASS" "$DBNAME" -e 'show tables;'
echo '--- staff'
mysql -u "$DBUSER" -p"$DBPASS" "$DBNAME" -e 'select staff_id,username,email,admin,isactive from ost_staff;'
echo '--- plugin'
mysql -u "$DBUSER" -p"$DBPASS" "$DBNAME" -e 'select * from ost_plugin;' 2>&1
echo '--- plugin_config'
mysql -u "$DBUSER" -p"$DBPASS" "$DBNAME" -e 'select * from ost_plugin_config;' 2>&1 | head -80
echo '--- version'
mysql -u "$DBUSER" -p"$DBPASS" "$DBNAME" -e 'select * from ost_config where namespace="core" and \`key\` in ("version","name","admin_email","default_email");' 2>&1
