<?php
/**
 * Create (or reset) a temporary osTicket administrator so the admin panel can
 * be verified from the outside. Intended for the lab VM only.
 */
chdir('/var/www/html/osticket');
require_once 'bootstrap.php';
require_once CLI_DIR . 'cli.inc.php';
Bootstrap::loadConfig();
Bootstrap::defineTables(TABLE_PREFIX);
Bootstrap::loadCode();
Bootstrap::connect();

require_once INCLUDE_DIR . 'class.staff.php';

$username = 'ocadmin';
$email = 'ocadmin@demo.lab';
$password = getenv('OST_TEMP_PW') ?: 'CHANGE_ME';

$staff = Staff::lookup($username);
if ($staff) {
    echo "existing staff id=", $staff->getId(), " -> resetting password\n";
} else {
    $vars = array(
        'username' => $username,
        'firstname' => 'Temp',
        'lastname' => 'Admin',
        'email' => $email,
        'phone' => '',
        'mobile' => '',
        'dept_id' => 1,
        'role_id' => 1,
        'isadmin' => 1,
        'isactive' => 1,
        'isvisible' => 1,
        'backend' => '',
        'passwd' => '',
    );
    $staff = Staff::create($vars);
    if (!$staff->save()) {
        fwrite(STDERR, "failed to save staff\n");
        exit(1);
    }
    echo "created staff id=", $staff->getId(), "\n";
}

$staff->setPassword($password, false);
$staff->isactive = 1;
$staff->isadmin = 1;
$staff->change_passwd = 0;
if (!$staff->save(true)) {
    fwrite(STDERR, "failed to save password\n");
    exit(1);
}

$check = Staff::lookup($username);
echo "verify: ", $check->getUsername(), " / ", $check->getEmail(),
     " / admin=", $check->isAdmin() ? 'yes' : 'no',
     " / active=", $check->isActive() ? 'yes' : 'no',
     " / backend=", var_export($check->backend, true), "\n";
echo "passwd-ok=", $check->cmp_passwd($password) ? 'yes' : 'no', "\n";
