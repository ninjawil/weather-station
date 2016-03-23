<?php
	$decoded = base64_decode($_POST['json']);
	$jsonFile = fopen('weather_data/config.json','w+');
	fwrite($jsonFile,$decoded);
	fclose($jsonFile);
	echo $decoded;
?>