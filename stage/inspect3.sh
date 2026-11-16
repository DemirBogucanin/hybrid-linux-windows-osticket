#!/bin/bash
set -u
CONF=/var/www/html/osticket/include/ost-config.php
DBPASS=$(grep -oP "define\('DBPASS',\s*'[^']*'" "$CONF" | sed "s/.*'\([^']*\)'$/\1/")
MYSQL="mysql -u osticket -p$DBPASS osticket"

echo '--- config namespaces'
$MYSQL -e 'select namespace, count(*) c from ost_config group by namespace order by c desc;'
echo '--- plugin-ish config'
$MYSQL -e "select namespace, \`key\`, value from ost_config where namespace like '%ldap%' or namespace like '%plugin%' or \`key\` like '%ldap%' order by namespace, \`key\`;"
echo '--- all config (non-core)'
$MYSQL -e "select namespace, \`key\`, value from ost_config where namespace <> 'core' order by namespace, \`key\` limit 200;"
echo '--- plugin table columns'
$MYSQL -e 'show columns from ost_plugin;'
echo '--- plugin rows'
$MYSQL -e 'select * from ost_plugin\G'
echo '--- syslog columns'
$MYSQL -e 'show columns from ost_syslog;'
echo '--- syslog last'
$MYSQL -e 'select * from ost_syslog order by log_id desc limit 20;' 2>&1 | head -60
echo '--- auth backend of staff'
$MYSQL -e 'select staff_id,username,backend,passwd from ost_staff;'
