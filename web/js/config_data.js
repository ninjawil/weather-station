//
// config_data.js
// Will De Freitas
//
// Reads and writes weather station configuration data
//
// 



//-------------------------------------------------------------------------------
// Once config data is loaded, draw it in Settings Modal
//-------------------------------------------------------------------------------
function updateSettingsModal(config_data) {


	$('#ip1').attr('value', config_data.network.ROUTER_IP);

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

	$('#garden-tag').attr('value', config_data.evernote.GARDENING_TAG);
	$('#plant-tag-id').attr('value', config_data.evernote.PLANT_TAG_ID);
	$('#location-tag-id').attr('value', config_data.evernote.LOCATION_TAG_ID);
	$('#state-tag-id').attr('value', config_data.evernote.STATE_TAG_ID);
	$('#notebook').attr('value', config_data.evernote.NOTEBOOK);

	$('#mk-addr').attr('value', config_data.maker_channel.MAKER_CH_ADDR);
	$('#mk-key').attr('value', config_data.maker_channel.MAKER_CH_KEY);

	
	if(config_data.irrigation.ALARM_ENABLE == 1){
		$('#irrig_alarm_en').prop('checked', true);
	} else {
		$('#irrig_alarm_en').prop('checked', false);
	}

	$('#irrig_alarm_lvl').attr('value', config_data.irrigation.ALARM_LEVEL);
	$('#irrig_coord_n').attr('value', config_data.irrigation.COORD_NORTH);
	$('#irrig_coord_s').attr('value', config_data.irrigation.COORD_SOUTH);
	$('#irrig_days').attr('value', config_data.irrigation.RECOMMENDED_WATERING_DAYS);
	$('#irrig_soil_type').val(config_data.irrigation.SOIL_TYPE);
	$('#irrig_crop_factor').attr('value', config_data.irrigation.CROP_FACTOR_KC);
	$('#irrig_root_depth').attr('value', config_data.irrigation.ROOT_DEPTH);
	$('#irrig_full').attr('value', config_data.irrigation.IRRIG_FULL);
	$('#irrig_partial').attr('value', config_data.irrigation.IRRIG_PARTIAL);

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
// Save data to JSON file
//-------------------------------------------------------------------------------
function saveSettings() {

    var heaterEnabled = 0;
    if ($('#heater-enable').is(":checked"))
	{
	  	heaterEnabled = 1;
	}

    var gwAlarm = 0;
    if ($('#irrig_alarm_en').is(":checked"))
	{
	  	gwAlarm = 1;
	}

	// router_ip = $('#settingsForm').find('[name="ip1"]').val()
	// router_ip = router_ip.concat(	'.',('#settingsForm').find('[name="ip2"]').val(),
	// 								'.',('#settingsForm').find('[name="ip3"]').val(),
	// 								'.',('#settingsForm').find('[name="ip4"]').val());

    var form_data = {
    	"network":{
    		"ROUTER_IP": 			$('#settingsForm').find('[name="ip1"]').val()	
    	},
	    "heater":{
	       "HEATER_ENABLE": 		heaterEnabled,
	       "HEATER_FORCE_ON": 		0,
	       "TEMP_HEATER_ON": 		Number($('#settingsForm').find('[name="heater-on-temp"]').val()),
	       "TEMP_HYSTERISIS":		Number($('#settingsForm').find('[name="heater-on-hyst"]').val()),
	       "MIPLUG_SENSOR_ID":		Number($('#settingsForm').find('[name="miplug-id"]').val())
	    },
	    "rain_gauge":{
	       "PRECIP_TICK_MEASURE": 	Number($('#settingsForm').find('[name="rain-gauge"]').val())
	    },
	    "thingspeak":{
	       "THINGSPEAK_HOST_ADDR": 	$('#settingsForm').find('[name="ts-host-addr"]').val(),
	       "THINGSPEAK_API_KEY": 	$('#settingsForm').find('[name="ts-api-key"]').val(),
	       "THINGSPEAK_CHANNEL_ID": Number($('#settingsForm').find('[name="ts-ch-id"]').val())
	    },
	    "maker_channel":{
	       "MAKER_CH_ADDR": 		$('#settingsForm').find('[name="mk-addr"]').val(),
	       "MAKER_CH_KEY": 			$('#settingsForm').find('[name="mk-key"]').val()
	    },
	    "irrigation":{
	    	  "ALARM_ENABLE": 		gwAlarm,
	       "ALARM_LEVEL": 			Number($('#settingsForm').find('[name="irrig_alarm_lvl"]').val()),
	       "COORD_NORTH": 			Number($('#settingsForm').find('[name="irrig_coord_n"]').val()),
	       "COORD_SOUTH": 			Number($('#settingsForm').find('[name="irrig_coord_s"]').val()),
	       "RECOMMENDED_WATERING_DAYS": Number($('#settingsForm').find('[name="irrig_days"]').val()),
	       "SOIL_TYPE": 			$('#settingsForm').find('[name="irrig_soil_type"]').val().toLowerCase(),
	       "CROP_FACTOR_KC": 		Number($('#settingsForm').find('[name="irrig_crop_factor"]').val()),
	       "ROOT_DEPTH": 			Number($('#settingsForm').find('[name="irrig_root_depth"]').val()),
	       "IRRIG_FULL": 			Number($('#settingsForm').find('[name="irrig_full"]').val()),
	       "IRRIG_PARTIAL": 		Number($('#settingsForm').find('[name="irrig_partial"]').val())
	    },
  		"evernote": {
		  	"GARDENING_TAG": 		$('#settingsForm').find('[name="garden-tag"]').val(),
		  	"PLANT_TAG_ID": 		$('#settingsForm').find('[name="plant-tag-id"]').val(),
		  	"LOCATION_TAG_ID": 		$('#settingsForm').find('[name="location-tag-id"]').val(),
		  	"STATE_TAG_ID": 		$('#settingsForm').find('[name="state-tag-id"]').val(),
		  	"NOTEBOOK": 			$('#settingsForm').find('[name="notebook"]').val()
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

	// grabConfigData();

	getFileData('weather_data/config.json', 'json', updateSettingsModal, []);

}

//===============================================================================
// Run on load
//===============================================================================

var config_data = null;

main();
