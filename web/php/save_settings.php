<?php
	$filename = $_SERVER['DOCUMENT_ROOT'] . '/weather_data/config.json';
	$decoded = base64_decode($_POST['json']);
	$jsonFile = fopen($filename,'w') or die("Unable to open file!");
	fwrite($jsonFile,$decoded);
	fclose($jsonFile);
	echo 'Data Saved';
?>