#!/bin/bash
set -u
MYSQL="mysql -u osticket -p${OST_DB_PW:?set OST_DB_PW} osticket"

echo '--- pre brisanja'
$MYSQL -e "select staff_id,username,email,backend from ost_staff;"

echo '--- pomocne tabele za staff 3'
$MYSQL -e "select * from ost_staff_dept_access where staff_id=3;" 2>&1
$MYSQL -e "select namespace, \`key\` from ost_config where namespace like 'staff.3%';" 2>&1

echo '--- brisanje ocadmin'
$MYSQL -e "delete from ost_staff_dept_access where staff_id=3;" 2>&1
$MYSQL -e "delete from ost_config where namespace like 'staff.3%';" 2>&1
$MYSQL -e "delete from ost_staff where username='ocadmin';" 2>&1

echo '--- posle brisanja'
$MYSQL -e "select staff_id,username,email,backend from ost_staff;"
