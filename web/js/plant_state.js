//
// plant_state.js
// Will De Freitas
//


//-------------------------------------------------------------------------------
// Once state data is loaded, draw it in State Modal
//-------------------------------------------------------------------------------
function updateStateModal(states) {

	console.log('run');


	var HTMLformState 	= '<form class="form-inline">%form%</form>',
		HTMLformItem 	= '<div class="form-group row"><label class="sr-only" for="%item_id%">%item_name%</label><div class="%size%"><input class="form-control form-control-sm" type="text" value="%value%" id="%item_id%" placeholder="%item_name%"></div></div>';

	var f_HTMLformItem = '';

	for (guid in states){

		f_HTMLformItem += 	HTMLformItem.replace(	'%item_id%', 	states[guid].name+'-name');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%item_name%', 'State Name');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%value%', 		states[guid].name); 
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%size%', 		'col-sm-3'); 

		f_HTMLformItem += 	HTMLformItem.replace(	'%item_id%', 	states[guid].name+'-guid');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%item_name%', 'GUID');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%value%', 		guid);
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%size%', 		'col-sm-5'); 

		f_HTMLformItem += 	HTMLformItem.replace(	'%item_id%', 	states[guid].name+'-symbol');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%item_name%', 'Symbol');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%value%', 		states[guid].symbol);
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%size%', 		'col-sm-2'); 

		f_HTMLformItem += 	HTMLformItem.replace(	'%item_id%', 	states[guid].name+'-color');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%item_name%', 'Color');
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%value%', 		states[guid].color);
		f_HTMLformItem = 	f_HTMLformItem.replace(	'%size%', 		'col-sm-2'); 

	
	}

	// Clear modal body area
	$('#modal_plant_state_body').empty();
	$('#modal_plant_state_body').append(HTMLformState.replace('%form%', f_HTMLformItem));


}


//-------------------------------------------------------------------------------
// Save data to JSON file
//-------------------------------------------------------------------------------
function saveState() {

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
		  	"STATE_TAG_ID": 		$('#settingsForm').find('[name="state-tag-id"]').val()
  		}
	};

    var json = JSON.stringify(form_data);
    var encoded = btoa(json);

	$.ajax({
		url: 	'php/save_file.php',
		type: 	"post",
		data: 	'file=' + '/weather_data/state_tags.json' +
				'json=' + encoded,
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

	getFileData('weather_data/state_tags.json', 'json', updateStateModal, []);

}

//===============================================================================
// Run on load
//===============================================================================

var config_data = null;

main();
