<?php
$result = shell_exec('/usr/bin/python /home/pi/weather/scripts/watchdog.py --clear');
echo $result;
?>