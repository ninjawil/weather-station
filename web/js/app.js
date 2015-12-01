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
function display_err(error_value) {

	var errors = {};
	errors = {
		1: ["Error", "There is an error!"],
		2: ["Error", "There is an error!"],
		3: ["Warning", "There is a warning!"],
		4: ["Error", "There is an error!"]
	};

	var formattedErrorMsg = HTMLerrorMSG.replace("%error_type%", errors[error_value][0]);
	formattedErrorMsg = formattedErrorMsg.replace("%error_msg%", "E"+ pad(error_value, 3) + " " + errors[error_value][1]);

	$('#error_display').append(formattedErrorMsg);
}

//-------------------------------------------------------------------------------
function display_time(t_since_epoch) {

	//Display time and date
	$('#update_time').append(HTMLupdateTime.replace("%time%", "00:00"));	
	$('#update_time').append(HTMLupdateDate.replace("%date%", "Thu 20 Dec 2015"));
}

//-------------------------------------------------------------------------------
function display_value(sensor_name, value, unit, description) {

	var formattedValueBox = HTMLvalueBox.replace("%id%", sensor_name);
	formattedValueBox = formattedValueBox.replace("%description%", description);


	//Display data
	$("#console").append(formattedValueBox);		


	var formattedValue = HTMLvalue.replace("%value%", value);
	formattedValue = formattedValue.replace("%unit%", unit);

	sensor_name = '#' + sensor_name;

	//Display data
	$(sensor_name).append(formattedValue);	
}


//===============================================================================
// MAIN
//===============================================================================
var system_error = 3;

var sensors = [];
sensors = [
	{
		'name': 'outside_temp',
		'description': 'Outside Temperature',
		'unit': '*C'
	},
	{
		'name': 'inside_temp',
		'description': 'Inside Temperature',
		'unit': '*C'
	},
	{
		'name': 'inside_hum',
		'description': 'Inside Humidity',
		'unit': '*C'
	},
	{
		'name': 'precip_rate',
		'description': 'Precipitation Rate',
		'unit': 'mm'
	},
	{
		'name': 'precip_acc',
		'description': 'Accumulated Precipitation',
		'unit': 'mm'
	},
	{
		'name': 'door_open',
		'description': 'Door Status',
		'unit': ''
	},
	{
		'name': 'heater_stat',
		'description': 'Heater Status',
		'unit': ''
	}
];

if(system_error > 0) {
	display_err(system_error);
};

display_time(10202020);

for(var i = 0, len = sensors.length; i < len; i++){
	display_value(sensors[i].name, 27.2, sensors[i].unit, sensors[i].description);
}
