//-------------------------------------------------------------------------------
//
// The MIT License (MIT)
//
// Copyright (c) 2015 William De Freitas
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
//-------------------------------------------------------------------------------


//===============================================================================
// Functions
//===============================================================================
function pad(num, size) {
    var s = "000" + num;
    return s.substr(s.length-size);
}


//-------------------------------------------------------------------------------
function displayErrorMessage(errorValue) {

	var errors = {};
	errors = {
		1: ["Error", "There is an error!"],
		2: ["Error", "There is an error!"],
		3: ["Warning", "There is a warning!"],
		4: ["Error", "There is an error!"]
	};

	var errorMessage = "E"+ pad(errorValue, 3) + " " + errors[errorValue][1];

	var formattedErrorMsg = HTMLerrorMSG.replace("%error_type%", errors[errorValue][0]);
	formattedErrorMsg = formattedErrorMsg.replace("%error_msg%", errorMessage);

	$('#error_display').append(formattedErrorMsg);
}


//-------------------------------------------------------------------------------
function displayTime(timeSinceEpoch) {

	//Convert time since epoch to human dates (time needs to be in milliseconds)
	var datetime = new Date(timeSinceEpoch * 1000);
	datetime = datetime.toUTCString();

	//Display time and date
	$('#update_time').append(HTMLupdateTime.replace("%time%", datetime.slice(17)));	
	$('#update_time').append(HTMLupdateDate.replace("%date%", datetime.slice(0, 17)));
}


//-------------------------------------------------------------------------------
function displayValue(sensors) {

	var formattedValueBox,
		formattedValue

	for(var sensor in sensors) {

		formattedValueBox = HTMLvalueBox.replace("%id%", sensor);
		formattedValueBox = formattedValueBox.replace("%description%", sensors[sensor].description);

		var arrayLength = sensors[sensor].readings.entry_value.length,
			value = 0;	

		switch(sensor) {
			case 'door_open':
				value = (sensors[sensor].readings.entry_value[arrayLength-2] >= 0.5) ? 'Open' : 'Closed';
				break;

			case 'heater_stat':
				value = (sensors[sensor].readings.entry_value[arrayLength-2] >= 0.5) ? 'On' : 'Off';
				break;

			default:
				value = sensors[sensor].readings.entry_value[arrayLength-2];
		}

		formattedValue = HTMLvalue.replace("%value%", value);
		formattedValue = formattedValue.replace("%unit%", sensors[sensor].unit);

		//Display data
		$("#sidebar").append(formattedValueBox);		
		$('#' + sensor).prepend(formattedValue);
	}

	displayTime(sensors['door_open'].readings.entry_time[sensors['door_open'].readings.entry_value.length-2]);
}


//-------------------------------------------------------------------------------
function xmlGetMetaData(filename, sensors) {

	var request = new XMLHttpRequest();

	request.open("GET", filename, false);
	request.send();

	var xml = request.responseXML;
	var xml_sensors  = xml.getElementsByTagName("entry");
	var xmlValue = xml.getElementsByTagName("row");

	for(var i = 0; i < xml_sensors.length; i++) {
		for(var j = 0; j < xmlValue.length; j++) {
			var xmlEntryValue = Number(xmlValue[j].childNodes[i+1].childNodes[0].nodeValue).toPrecision(4),
				xmlEntryTime = Number(xmlValue[j].childNodes[0].childNodes[0].nodeValue);
			sensors[xml_sensors[i].childNodes[0].nodeValue].readings.entry_time.push(xmlEntryTime); 
			sensors[xml_sensors[i].childNodes[0].nodeValue].readings.entry_value.push(xmlEntryValue);
		}
	}

	return sensors;
}

//-------------------------------------------------------------------------------
function main() {

	var systemError = 3,
		sensors = { 'outside_temp': {
						description: 'Outside Temperature',
						unit: '°C',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'inside_temp': {
						description: 'Inside Temperature',
						unit: '°C',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'inside_hum': {
						description: 'Inside Humidity',
						unit: '°C',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'precip_rate': {
						description: 'Precipitation Rate',
						unit: 'mm',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'precip_acc': {
						description: 'Accumulated Precipitation',
						unit: 'mm',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'door_open': {
						description: 'Door Status',
						unit: '',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'heater_stat': {
						description: 'Heater Status',
						unit: '',
						readings: {
							entry_time: [],
							entry_value: []
						}
					}
				};

	if(systemError) {
		displayErrorMessage(systemError);
	};

	var sensors = xmlGetMetaData("data/weather3h.xml", sensors);

	displayValue(sensors);
	
}


//===============================================================================
// Main
//===============================================================================

main();
