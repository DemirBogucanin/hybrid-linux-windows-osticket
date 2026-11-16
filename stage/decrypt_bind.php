<?php
define('INCLUDE_DIR', '/var/www/html/osticket/include/');
define('PEAR_DIR', INCLUDE_DIR . 'pear/');
require_once INCLUDE_DIR . 'ost-config.php';
require_once INCLUDE_DIR . 'class.crypto.php';

$value = '$2$JDEkHfSaZFuwEin8ulUQ0rxEwjFs1UD5lfOOCQ4IfWOtmng=';
$ns = 'plugin.1.instance.2';
$plain = Crypto::decrypt($value, SECRET_SALT, $ns);
if ($plain === false) {
    fwrite(STDERR, "decrypt failed\n");
    exit(1);
}
echo $plain, "\n";
