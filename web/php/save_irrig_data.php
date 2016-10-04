<?php
	$filename = $_SERVER['DOCUMENT_ROOT'] . '/weather_data/irrigation.json';
	$decoded = base64_decode($_POST['json']);
	$jsonFile = fopen($filename,'w') or die("Unable to open file!");
	fwrite($jsonFile,$decoded);
	fclose($jsonFile);
	// $command = escapeshellcmd('/usr/bin/python2.7 /home/pi/weather/scripts/irrigation.py --irrigated');
	// $output = shell_exec($command);
	// echo $output;
?>