//-------------------------------------------------------------------------------
// Grab config.json data
//-------------------------------------------------------------------------------
function grabConfigData(){

	$.getJSON('weather_data/config.json', function(json) {
	    updateSettingsModal(json);
	});

}


//-------------------------------------------------------------------------------
// Once config data is loaded, draw it in Settings Modal
//-------------------------------------------------------------------------------
function updateSettingsModal(config_data) {

	if(config_data.heater.HEATER_ENABLE == 1){
		$('#heater-enable').attr('placeholder', 'checked');		
	}

	$('#heater-on-temp').attr('placeholder', config_data.heater.TEMP_HEATER_ON);
	$('#heater-on-hyst').attr('placeholder', config_data.heater.TEMP_HYSTERISIS);
	$('#miplug-id').attr('placeholder', config_data.heater.MIPLUG_SENSOR_ID);

}


//-------------------------------------------------------------------------------
// Prepares data and displays it on web load
//-------------------------------------------------------------------------------
function main() {

	grabConfigData();

}

//===============================================================================
// Run on load
//===============================================================================
main();
