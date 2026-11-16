<?php
/**
 * Reset the password of the primary osTicket administrator (`dadmin`) to a
 * known value, so the lab has a usable admin account after the temporary one
 * was removed.
 */
chdir('/var/www/html/osticket');
require_once 'bootstrap.php';
require_once CLI_DIR . 'cli.inc.php';
Bootstrap::loadConfig();
Bootstrap::defineTables(TABLE_PREFIX);
Bootstrap::loadCode();
Bootstrap::connect();

require_once INCLUDE_DIR . 'class.staff.php';

$password = getenv('OST_ADMIN_PW') ?: 'CHANGE_ME';
$staff = Staff::lookup('dadmin');
if (!$staff) {
    fwrite(STDERR, "dadmin not found\n");
    exit(1);
}

$staff->setPassword($password, false);
$staff->change_passwd = 0;
$staff->isactive = 1;
if (!$staff->save(true)) {
    fwrite(STDERR, "save failed\n");
    exit(1);
}

$check = Staff::lookup('dadmin');
printf("dadmin: admin=%s active=%s backend=%s passwd-ok=%s\n",
    $check->isAdmin() ? 'yes' : 'no',
    $check->isActive() ? 'yes' : 'no',
    var_export($check->backend, true),
    $check->cmp_passwd($password) ? 'yes' : 'no');
