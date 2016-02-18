$decoded = base64_decode($_POST['json'])
$jsonFile = fopen('config.json','w+');
fwrite($jsonFile,$decoded);
fclose($jsonFile);