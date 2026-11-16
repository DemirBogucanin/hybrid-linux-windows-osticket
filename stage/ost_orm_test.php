<?php
chdir('/var/www/html/osticket');
require_once 'bootstrap.php';
require_once CLI_DIR . 'cli.inc.php';
Bootstrap::loadConfig();
Bootstrap::defineTables(TABLE_PREFIX);
Bootstrap::loadCode();
Bootstrap::connect();
require_once INCLUDE_DIR . 'class.staff.php';

$s = Staff::lookup(1);
if (!$s) {
    echo "none\n";
    exit(1);
}
echo $s->getUsername(), " / ", $s->getEmail(), " / admin=", $s->isAdmin() ? 'yes' : 'no', "\n";
