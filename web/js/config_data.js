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
function updateSettingsModal(json) {

    config_data = json;

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

	$('#heater-on-temp').attr('value', config_data.heater.TEMP_HEATER_ON);
	$('#heater-on-hyst').attr('value', config_data.heater.TEMP_HYSTERISIS);
	$('#miplug-id').attr('value', config_data.heater.MIPLUG_SENSOR_ID);

	$('#rain-gauge').attr('value', config_data.rain_gauge.PRECIP_TICK_MEASURE);

	$('#ts-host-addr').attr('value', config_data.thingspeak.THINGSPEAK_HOST_ADDR);
	$('#ts-api-key').attr('value', config_data.thingspeak.THINGSPEAK_API_KEY);
	$('#ts-ch-id').attr('value', config_data.thingspeak.THINGSPEAK_CHANNEL_ID);

	$('#mk-addr').attr('value', config_data.maker_channel.MAKER_CH_ADDR);
	$('#mk-key').attr('value', config_data.maker_channel.MAKER_CH_KEY);

	
	if(config_data.water_level.ALARM_ENABLE == 1){
		$('#gw-enable').prop('checked', true);
	} else {
		$('#gw-enable').prop('checked', false);
	}

	$('#gw_rec_water_vol').attr('value', config_data.water_level.RECOMMENDED_WATERING);
	$('#gw_rec_water_days').attr('value', config_data.water_level.RECOMMENDED_WATERING_DAYS);
	$('#gw_water_sat').attr('value', config_data.water_level.GRND_WATER_SATURATION);
	$('#gw_dry_rate_0').attr('value', config_data.water_level.DRY_RATE_0_9);
	$('#gw_dry_rate_1').attr('value', config_data.water_level.DRY_RATE_10_19);
	$('#gw_dry_rate_2').attr('value', config_data.water_level.DRY_RATE_20_29);
	$('#gw_dry_rate_3').attr('value', config_data.water_level.DRY_RATE_30_UP);


    $(function(){
        $('#checkbox input:checkbox').on('change', function(){
            if($(this).is(':checked')) {
                $('#heater-enable').prop('checked', true);
                $('#heater-on-hyst').prop('disabled', false);
                $('#miplug-id').prop('disabled', false);
                $('#heater-on-temp').prop('disabled', false);
            } else {
                $('#heater-enable').prop('checked', false);
                $('#heater-on-hyst').prop('disabled', true);
                $('#miplug-id').prop('disabled', true);
                $('#heater-on-temp').prop('disabled', true);                
            }
        });
    });

}


//-------------------------------------------------------------------------------
// Once config data is loaded, draw it in Settings Modal
//-------------------------------------------------------------------------------
function saveSettings() {

    var heaterEnabled = 0;
    if ($('#heater-enable').is(":checked"))
	{
	  	heaterEnabled = 1;
	}

    var gwAlarm = 0;
    if ($('#gw-enable').is(":checked"))
	{
	  	gwAlarm = 1;
	}

    var form_data = {
	   "heater":{
	      "HEATER_ENABLE": 		heaterEnabled,
	      "HEATER_FORCE_ON": 	0,
	      "TEMP_HEATER_ON": 	Number($('#settingsForm').find('[name="heater-on-temp"]').val()),
	      "TEMP_HYSTERISIS":	Number($('#settingsForm').find('[name="heater-on-hyst"]').val()),
	      "MIPLUG_SENSOR_ID":	Number($('#settingsForm').find('[name="miplug-id"]').val())
	   },
	   "rain_gauge":{
	      "PRECIP_TICK_MEASURE": Number($('#settingsForm').find('[name="rain-gauge"]').val())
	   },
	   "thingspeak":{
	      "THINGSPEAK_HOST_ADDR": 	$('#settingsForm').find('[name="ts-host-addr"]').val(),
	      "THINGSPEAK_API_KEY": 	$('#settingsForm').find('[name="ts-api-key"]').val(),
	      "THINGSPEAK_CHANNEL_ID": 	Number($('#settingsForm').find('[name="ts-ch-id"]').val())
	   },
	   "maker_channel":{
	      "MAKER_CH_ADDR": 	$('#settingsForm').find('[name="mk-addr"]').val(),
	      "MAKER_CH_KEY": 	$('#settingsForm').find('[name="mk-key"]').val()
	   },
	   "water_level":{
	   	  "ALARM_ENABLE": 				gwAlarm,
	      "RECOMMENDED_WATERING": 		Number($('#settingsForm').find('[name="gw_rec_water_vol"]').val()),
	      "RECOMMENDED_WATERING_DAYS": 	Number($('#settingsForm').find('[name="gw_rec_water_days"]').val()),
	      "GRND_WATER_SATURATION": 		Number($('#settingsForm').find('[name="gw_water_sat"]').val()),
	      "DRY_RATE_0_9": 				Number($('#settingsForm').find('[name="gw_dry_rate_0"]').val()),
	      "DRY_RATE_10_19": 			Number($('#settingsForm').find('[name="gw_dry_rate_1"]').val()),
	      "DRY_RATE_20_29": 			Number($('#settingsForm').find('[name="gw_dry_rate_2"]').val()),
	      "DRY_RATE_30_UP": 			Number($('#settingsForm').find('[name="gw_dry_rate_3"]').val())
	   }
	};

    var json = JSON.stringify(form_data);
    var encoded = btoa(json);

	$.ajax({
		url: 'php/save_settings.php',
		type: "post",
		data: 'json=' + encoded,
		success: function(rxData) {
			alert(rxData);
	  }
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

var config_data = null;

main();
