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
		$('#heater-enable').prop('checked', true);
		$('#heater-on-temp').prop('disabled', false);
		$('#heater-on-hyst').prop('disabled', false);
		$('#miplug-id').prop('disabled', false);
	} else {
		$('#heater-enable').prop('checked', false);
		$('#heater-on-temp').prop('disabled', true);
		$('#heater-on-hyst').prop('disabled', true);
		$('#miplug-id').prop('disabled', true);	
	}

	$('#heater-on-temp').attr('placeholder', config_data.heater.TEMP_HEATER_ON);
	$('#heater-on-hyst').attr('placeholder', config_data.heater.TEMP_HYSTERISIS);
	$('#miplug-id').attr('placeholder', config_data.heater.MIPLUG_SENSOR_ID);

	$('#rain-gauge').attr('placeholder', config_data.rain_gauge.PRECIP_TICK_MEASURE);

	$('#ts-host-addr').attr('placeholder', config_data.thingspeak.THINGSPEAK_HOST_ADDR);
	$('#ts-api-key').attr('placeholder', config_data.thingspeak.THINGSPEAK_API_KEY);
	$('#ts-ch-id').attr('placeholder', config_data.thingspeak.THINGSPEAK_CHANNEL_ID);


	$(function(){
	    $('#chkboxes input:checkbox').on('change', function(){
	        if($(this).is(':checked'))
	        {
	        	$('#heater-enable').prop('checked', true);
	            $('#heater-on-temp').prop('disabled', false);
	        }
	        else
	        {
	            $('#heater-enable').prop('checked', false);
	            $('#heater-on-temp').prop('disabled', true);
	        }
	    });​
	});

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
