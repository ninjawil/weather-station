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
// return everything after the question mark
function getUrlParameter() {
         
    idx = window.location.href.indexOf("?");
    
    if( idx < 0 ) {
    	return "";
    } else {
    	return window.location.href.substring(idx + 1);
    }
    
}


//-------------------------------------------------------------------------------
// Manages error messages depending on passed error code
function displayErrorMessage(errorValue) {

	var errors = {};
	errors = {
		1: ["Error", "There is an error!"],
		2: ["Error", "There is an error!"],
		3: ["Warning", "There is a warning!"],
		4: ["Error", "There is an error!"]
	};

	var errorMessage = errors[errorValue][0] + " E"+ pad(errorValue, 3) + ": ";

	var formattedErrorMsg = HTMLerrorMSG.replace("%error_type%", errorMessage);
	formattedErrorMsg = formattedErrorMsg.replace("%error_msg%", errors[errorValue][1]);

	$('#error_display').append(formattedErrorMsg);
}


//-------------------------------------------------------------------------------
// Converts time since last epoch and displays it on the webpage
function displayTime(timeSinceEpoch) {

	//Convert time since epoch to human dates (time needs to be in milliseconds)
	var datetime = new Date(timeSinceEpoch * 1000);
	datetime = datetime.toUTCString();

	//Display time and date
	$('#update_time').append(HTMLupdateTime.replace("%time%", datetime.slice(17)));	
	$('#update_time').append(HTMLupdateDate.replace("%date%", datetime.slice(0, 17)));
}


//-------------------------------------------------------------------------------
// Displays last updated values on web page
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

	// Display last update time
	displayTime(sensors['door_open'].readings.entry_time[sensors['door_open'].readings.entry_value.length-2]);
}


//-------------------------------------------------------------------------------
// Gets data from XML file and parses it to sensors array
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
// Gets data from log file
function logGetData(directory, filename) {

	$.ajax({
        async:false,
        url: directory + '_logs/' + filename,
        dataType: 'text',
        success: function(data) 
        	{
	        	$('#' + filename.slice(0, -4)).append(data);
            }
        });
}


//-------------------------------------------------------------------------------
// Organizes log boxes in modal
function displayLogData(directory, filenames) {

	var columnNumber = 1,
		formattedHTMLlogBox = '';

	for(var logFile in filenames) {

		//Prepare HTML with log file details
		formattedHTMLlogBox = HTMLlogBox.replace('%logFileName%', filenames[logFile]);
		formattedHTMLlogBox = formattedHTMLlogBox.replace('%logName%', filenames[logFile].slice(0, -4));
		$('#log_modal_col_' + columnNumber).append(formattedHTMLlogBox);

		//Write log data
		logGetData(directory, filenames[logFile]);

		//Alternate columns
		columnNumber = (columnNumber === 1) ? 2 : 1;
	}
}

//-------------------------------------------------------------------------------
// Displays graph
function displayGraph(sensors) {

	//Consolidate data
	var seriesSetup = [];

	for (sensor in sensors) {
		var data = [],
			axis = 0;
		for(var i = 0; i < sensors[sensor].readings.entry_time.length; i++) {
			if(sensors[sensor].readings.entry_value[i] != 'NaN') {
				data.push([Number(sensors[sensor].readings.entry_time[i])*1000, Number(sensors[sensor].readings.entry_value[i])]);
			}
		}

		if(sensors[sensor].unit === '%') {
			axis = 1;
		} else if(sensors[sensor].unit === 'mm') {
			axis = 2;
		}

		seriesSetup.push({
			name: sensor,
			type: sensors[sensor].graph,
            data : data,
            yAxis: axis,
            tooltip: {
	            valueDecimals: 2
	        }
		});
	}

	console.log(seriesSetup);

	//Display graph

	highchartOptions = {
			chart: 	{
		            	renderTo: 'container'
					},
			title: 	{
                        text: null
                    },
            xAxis: 	{
		            	type: 'datetime',
		            	crosshair: true
		            },

		    yAxis: [{ // Primary yAxis
		            	labels: {
		                			format: '{value}°C',
		                			style: 	{
		                    					color: Highcharts.getOptions().colors[1]
		                					}
		            			},
		            	title: 	{
		                			text: 'Temperature',
					                style: 	{
					                    		color: Highcharts.getOptions().colors[1]
					                		}
		            			}
		        	}, { // Secondary yAxis
		           		labels: {
		                			format: '{value}%',
		                			style: 	{
		                    					color: Highcharts.getOptions().colors[1]
		                					}
		            			},
		            	title: 	{
		                			text: 'Humidity',
					                style: 	{
					                    		color: Highcharts.getOptions().colors[1]
					                		}
		            			},
		            	opposite: true
		        	}, { // Third yAxis
		           		labels: {
		                			format: '{value}mm',
		                			style: 	{
		                    					color: Highcharts.getOptions().colors[1]
		                					}
		            			},
		            	title: 	{
		                			text: 'Rainfall',
					                style: 	{
					                    		color: Highcharts.getOptions().colors[1]
					                		}
		            			},
		            	opposite: true
		        	}],

            series: seriesSetup
    };

	$('#graph-container').highcharts(highchartOptions);

}


//-------------------------------------------------------------------------------
// Prepares data and displays it
function main() {

	var systemError = 0,
		dir = 'weather',
		logFiles = ['read_sensors.log', 'read_rain_gauge.log', 'rrd_export.log', 'rrd_ts_sync.log'],
		dataFiles = {'':   'wd_last_3h.xml',
					 '3h': 'wd_last_3h.xml',
					 '1d': 'wd_avg_1d.xml',
					 '2d': 'wd_avg_2d.xml',
					 '1w': 'wd_avg_1w.xml',
					 '1m': 'wd_avg_1m.xml',
					 '3m': 'wd_avg_3m.xml',
					 '1y': 'wd_avg_1y.xml',
					 '1y': 'wd_min_1y.xml',
					 '1y': 'wd_max_1y.xml'
				    },
		sensors = { 'outside_temp': {
						description: 'Outside Temperature',
						unit: '°C',
						graph: 'line',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'inside_temp': {
						description: 'Inside Temperature',
						unit: '°C',
						graph: 'line',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'inside_hum': {
						description: 'Inside Humidity',
						unit: '%',
						graph: 'line',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'precip_rate': {
						description: 'Precipitation Rate',
						unit: 'mm',
						graph: 'column',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'precip_acc': {
						description: 'Accumulated Precipitation',
						unit: 'mm',
						graph: 'line',
						readings: {
							entry_time: [],
							entry_value: []
						}
					},
					'door_open': {
						description: 'Door Status',
						unit: '',
						graph: 'line',
						readings: {
							entry_time: [],
							entry_value: []
						}
					}
					// 'heater_stat': {
					// 	description: 'Heater Status',
					// 	unit: '',
					// 	readings: {
					// 		entry_time: [],
					// 		entry_value: []
					// 	}
					// }
				};

	if(systemError) {
		displayErrorMessage(systemError);
	};

	var sensors = xmlGetMetaData(dir + "_data/" + dataFiles[getUrlParameter()] , sensors);

	displayValue(sensors);
	displayLogData(dir, logFiles);
	//displayGraph(sensors);


	// Highlights correct navbar location
	var url = window.location;
	$('ul.nav a').filter(function() {
		return this.href == url;
	}).parent().addClass('active');


	/*
The purpose of this demo is to demonstrate how multiple charts on the same page can be linked
through DOM and Highcharts events and API methods. It takes a standard Highcharts config with a
small variation for each data set, and a mouse/touch event handler to bind the charts together.
*/

	$(function () {

	    /**
	     * In order to synchronize tooltips and crosshairs, override the
	     * built-in events with handlers defined on the parent element.
	     */
	    $('#graph-container').bind('mousemove touchmove', function (e) {
	        var chart,
	            point,
	            i;

	        for (i = 0; i < Highcharts.charts.length; i = i + 1) {
	            chart = Highcharts.charts[i];
	            e = chart.pointer.normalize(e); // Find coordinates within the chart
	            point = chart.series[0].searchPoint(e, true); // Get the hovered point

	            if (point) {
	                point.onMouseOver(); // Show the hover marker
	                chart.tooltip.refresh(point); // Show the tooltip
	                chart.xAxis[0].drawCrosshair(e, point); // Show the crosshair
	            }
	        }
	    });
	    /**
	     * Override the reset function, we don't need to hide the tooltips and crosshairs.
	     */
	    Highcharts.Pointer.prototype.reset = function () {
	        return undefined;
	    };

	    /**
	     * Synchronize zooming through the setExtremes event handler.
	     */
	    function syncExtremes(e) {
	        var thisChart = this.chart;

	        if (e.trigger !== 'syncExtremes') { // Prevent feedback loop
	            Highcharts.each(Highcharts.charts, function (chart) {
	                if (chart !== thisChart) {
	                    if (chart.xAxis[0].setExtremes) { // It is null while updating
	                        chart.xAxis[0].setExtremes(e.min, e.max, undefined, false, { trigger: 'syncExtremes' });
	                    }
	                }
	            });
	        }
	    }

	    // Get the data. The contents of the data file can be viewed at
	    // https://github.com/highcharts/highcharts/blob/master/samples/data/activity.json
	    $.getJSON('https://www.highcharts.com/samples/data/jsonp.php?filename=activity.json&callback=?', function (activity) {
	        $.each(activity.datasets, function (i, dataset) {

	            // Add X values
	            dataset.data = Highcharts.map(dataset.data, function (val, j) {
	                return [activity.xData[j], val];
	            });

	            $('<div class="chart">')
	                .appendTo('#graph-container')
	                .highcharts({
	                    chart: {
	                        marginLeft: 40, // Keep all charts left aligned
	                        spacingTop: 20,
	                        spacingBottom: 20,
	                        zoomType: 'x'
	                    },
	                    title: {
	                        text: dataset.name,
	                        align: 'left',
	                        margin: 0,
	                        x: 30
	                    },
	                    credits: {
	                        enabled: false
	                    },
	                    legend: {
	                        enabled: false
	                    },
	                    xAxis: {
	                        crosshair: true,
	                        events: {
	                            setExtremes: syncExtremes
	                        },
	                        labels: {
	                            format: '{value} km'
	                        }
	                    },
	                    yAxis: {
	                        title: {
	                            text: null
	                        }
	                    },
	                    tooltip: {
	                        positioner: function () {
	                            return {
	                                x: this.chart.chartWidth - this.label.width, // right aligned
	                                y: -1 // align to title
	                            };
	                        },
	                        borderWidth: 0,
	                        backgroundColor: 'none',
	                        pointFormat: '{point.y}',
	                        headerFormat: '',
	                        shadow: false,
	                        style: {
	                            fontSize: '18px'
	                        },
	                        valueDecimals: dataset.valueDecimals
	                    },
	                    series: [{
	                        data: dataset.data,
	                        name: dataset.name,
	                        type: dataset.type,
	                        color: Highcharts.getOptions().colors[i],
	                        fillOpacity: 0.3,
	                        tooltip: {
	                            valueSuffix: ' ' + dataset.unit
	                        }
	                    }]
	                });
	        });
	    });
	});

}


//===============================================================================
// Main
//===============================================================================

main();

