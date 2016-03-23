<?php
$result = shell_exec('python /home/pi/weather/scripts/watchdog.py --clear');
echo $result;
?>