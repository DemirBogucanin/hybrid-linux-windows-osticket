#!/bin/bash
set -u
echo '--- apache'
apache2 -v | head -1
echo '--- php'
php -v | head -1
echo '--- mariadb'
mariadb --version 2>/dev/null || mysql --version
echo '--- osticket version/config'
mysql -u osticket -p"${OST_DB_PW:?set OST_DB_PW}" osticket -e "select namespace, \`key\`, value from ost_config where namespace='core' and \`key\` in ('version','name','helpdesk_title','admin_email','default_email','url');" 2>&1
echo '--- staff'
mysql -u osticket -p"${OST_DB_PW:?set OST_DB_PW}" osticket -e "select staff_id,username,email,backend,isadmin,lastlogin from ost_staff order by staff_id;" 2>&1
echo '--- ldap plugin version'
mysql -u osticket -p"${OST_DB_PW:?set OST_DB_PW}" osticket -e "select id,name,version,isactive from ost_plugin;" 2>&1
echo '--- user created via LDAP'
mysql -u osticket -p"${OST_DB_PW:?set OST_DB_PW}" osticket -e "select u.id,u.name,e.address from ost_user u join ost_user_email e on e.id=u.default_email_id;" 2>&1
