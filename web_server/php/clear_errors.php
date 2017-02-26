<?php
$command = escapeshellcmd('/usr/bin/python2.7 /home/pi/weather/scripts/watchdog.py --clear');
$output = shell_exec($command);
echo $output;
?>