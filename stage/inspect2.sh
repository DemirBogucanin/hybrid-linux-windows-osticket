#!/bin/bash
set -u
CONF=/var/www/html/osticket/include/ost-config.php
DBPASS=$(grep -oP "define\('DBPASS',\s*'[^']*'" "$CONF" | sed "s/.*'\([^']*\)'$/\1/")
MYSQL="mysql -u osticket -p$DBPASS osticket"

echo '--- staff columns'
$MYSQL -e 'show columns from ost_staff;'
echo '--- staff rows'
$MYSQL -e 'select staff_id,username,firstname,lastname,email,isactive,role_id,created,lastlogin from ost_staff;'
echo '--- roles'
$MYSQL -e 'select id,name,flags from ost_role;'
echo '--- plugin_instance columns'
$MYSQL -e 'show columns from ost_plugin_instance;'
echo '--- plugin_instance rows'
$MYSQL -e 'select * from ost_plugin_instance\G'
echo '--- config core'
$MYSQL -e "select namespace, \`key\`, value from ost_config where namespace='core' and \`key\` in ('version','name','admin_email','default_email','helpdesk_title','url');"
echo '--- last syslog'
$MYSQL -e 'select * from ost_syslog order by id desc limit 20;' 2>&1 | head -60
echo '--- apache osticket log'
grep -i osticket /var/log/apache2/access.log 2>/dev/null | tail -20
