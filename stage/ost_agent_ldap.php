<?php
/**
 * Point the existing osTicket agent `tdelic` at the Active Directory backend so
 * the agent signs in with the domain password instead of a local one.
 */
chdir('/var/www/html/osticket');
require_once 'bootstrap.php';
require_once CLI_DIR . 'cli.inc.php';
Bootstrap::loadConfig();
Bootstrap::defineTables(TABLE_PREFIX);
Bootstrap::loadCode();
Bootstrap::connect();

require_once INCLUDE_DIR . 'class.staff.php';

$staff = Staff::lookup('tdelic');
if (!$staff) {
    fwrite(STDERR, "agent tdelic not found\n");
    exit(1);
}

printf("before: username=%s backend=%s email=%s admin=%s active=%s\n",
    $staff->getUsername(), var_export($staff->backend, true), $staff->getEmail(),
    $staff->isAdmin() ? 'yes' : 'no', $staff->isActive() ? 'yes' : 'no');

$staff->backend = 'ldap.p1i2';
if (!$staff->save(true)) {
    fwrite(STDERR, "save failed\n");
    exit(1);
}

$check = Staff::lookup('tdelic');
$backend = $check->getAuthBackend();
printf("after:  backend=%s backend-name=%s\n",
    var_export($check->backend, true),
    $backend ? $backend->getName() : '(none)');
