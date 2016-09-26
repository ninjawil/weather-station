//
// charts_update.js
// Will De Freitas
//
// Draws charts based on xml files
//
// 

//-------------------------------------------------------------------------------
// Return passed object
//-------------------------------------------------------------------------------
function cloneObject(obj) {
    return jQuery.extend(true, {}, obj);
}


//-------------------------------------------------------------------------------
// Converts time since last epoch and displays it on the webpage
//-------------------------------------------------------------------------------
function displayTime(timeSinceEpoch) {

	//Convert time since epoch to human dates (time needs to be in milliseconds)
	var datetime = new Date(timeSinceEpoch);
	// datetime = datetime.toString();
	// datetime = datetime.toUTCString();

	var time = datetime.toLocaleTimeString();

	if(datetime.getTimezoneOffset() == "-60") {
		time = time.concat(" &#x263C;");
	}

	//Display time and date
	$('#update_time').append(HTMLupdateTime.replace("%time%", time));	
	$('#update_time').append(HTMLupdateDate.replace("%date%", datetime.toUTCString().slice(0, 17)));
}


//-------------------------------------------------------------------------------
// Displays last updated values on web page
//-------------------------------------------------------------------------------
function sidebarData(sensors) {

	var formattedValueBox,
		formattedValue;

	for(var sensor in sensors) {

		formattedValueBox = HTMLvalueBox.replace("%id%", sensor);
		formattedValueBox = formattedValueBox.replace("%description%", sensors[sensor].description);

		var arrayLength = sensors[sensor].readings.length,
			value = 0;

		// Do not display if sesnsor has no values
		if(arrayLength > 0){	

			switch(sensor) {
				case 'door_open':
					value = (sensors[sensor].readings[arrayLength-1][1] >= 0.5) ? 'Open' : 'Closed';
					break;

				case 'sw_status':
					value = (sensors[sensor].readings[arrayLength-1][1] >= 0.5) ? 'On' : 'Off';
					break;

				default:
					value = sensors[sensor].readings[arrayLength-1][1].toPrecision(4);
			}

			formattedValue = HTMLvalue.replace("%value%", value);
			formattedValue = formattedValue.replace("%unit%", sensors[sensor].unit);

			//Display data
			$("#sidebar").append(formattedValueBox);		
			$('#' + sensor).prepend(formattedValue);
		}
	}

	// Display last update time
	displayTime(sensors['door_open'].readings[sensors['door_open'].readings.length-1][0]);
}


//-------------------------------------------------------------------------------
// Displays last updated values on web page
//-------------------------------------------------------------------------------
function formatAllDropdown(sensors) {

	var formattedDropdown;

	for(var sensor in sensors) {

		formattedDropdown = HTMLallDropdown.replace("%id%", "'" + sensor + "'");
		formattedDropdown = formattedDropdown.replace("%name%", sensors[sensor].description);

		//Display data		
		$('#allDropdown').append(formattedDropdown);
	}
}



//-------------------------------------------------------------------------------
// Gets data from XML file
//-------------------------------------------------------------------------------
function xmlGetData(filename, sensors_array, functionCall, args) {

	var xhttp = new XMLHttpRequest();

	var output_data = {};

	xhttp.onreadystatechange = function() {
	    if (xhttp.readyState == 4 && xhttp.status == 200) {

			var xml = xhttp.responseXML,
				xml_sensors  = xml.getElementsByTagName("entry"),
				xmlValue = xml.getElementsByTagName("row");

			for(var i = 0; i < xml_sensors.length; i++) {

				output_data[xml_sensors[i].childNodes[0].nodeValue] = [];

				for(var j = 0; j < xmlValue.length; j++) {
					var xmlEntryValue = xmlValue[j].childNodes[i+1].childNodes[0].nodeValue,
						xmlEntryTime = xmlValue[j].childNodes[0].childNodes[0].nodeValue;

					if(xmlEntryValue != 'NaN'){
						output_data[xml_sensors[i].childNodes[0].nodeValue].push([Number(xmlEntryTime*1000), Number(xmlEntryValue)]); 
					}
				}
			}

			// If sensor object passed then return it otherwise return raw data
			if (sensors_array !== ""){
				for(var sensor in output_data) {
					sensors_array[sensor].readings = output_data[sensor];
				}
				args.push(sensors_array);
			} else {
				args.push(output_data);
			}

			//args.push(true); // Display day and night color

			functionCall.apply(this, args);

	    }
	 };

	xhttp.open("GET", filename, true);
	xhttp.send();


}


//-------------------------------------------------------------------------------
// Display heat map
//-------------------------------------------------------------------------------
function displayHeatMap(sensor_id) {

	// Called from index.html
	// Highlights the appropriate button and clears working screen area
	// 

	// Highlights correct navbar location
	$('li').removeClass('active');
	$('#calendar').parent().addClass('active');

	// Clear chart area
	$('#graph-container').empty();

    // Set up chart screen sections
    $('<div id="title-section"></div>').appendTo('#graph-container');
    $('<div id="charts-section"><div id="charts-col1" class="col-md-1"></div><div id="charts-col2" class="col-md-11"></div></div>').appendTo('#graph-container');

	xmlGetData(dir + '_data/' + dataFiles['1y'], '', drawHeatMap, [sensor_id]);
    
}


//-------------------------------------------------------------------------------
// Draw heat map
//-------------------------------------------------------------------------------
function drawHeatMap(sensor_name, value_array) {


	// Create chart
	var title = '<div class="row"><h4>%name%</h4></div><div id="cal-heatmap"></div>';
    $(title.replace("%name%", sensor_setup[sensor_name].description)).appendTo('#title-section');

	var date = '<div class="vertical-text"><h4>%date%</h4></div>';
    $(date.replace("%date%", '2016')).appendTo('#charts-col1');


    var parser = function(data) {
		var stats = {};
		for (var d in data) {
			stats[data[d][0]/1000] = data[d][1];
		}
		return stats;
	};

	var data_array = [];
	for(var i = 0; i<value_array[sensor_name].length; i++){
	    data_array[i] = value_array[sensor_name][i][1];
	}
	var max_of_array = Math.max.apply(Math, data_array);
	var min_of_array = Math.min.apply(Math, data_array);
	var legend_range = [];

	for(var i = 0; i < 4; i++) {
		legend_range[i] = ((i+2)* (max_of_array - min_of_array))/5;
	}

	var calendar = new CalHeatMap();
	calendar.init({
		itemSelector: "#charts-col2",
		data: value_array[sensor_name],
		afterLoadData: parser,
		itemName: [sensor_setup[sensor_name].unit, sensor_setup[sensor_name].unit],
		start: new Date(2016, 0),
		domain : "month",			// Group data by month
		subDomain : "day",			// Split each month by days
		cellsize: 20,
		cellpadding: 3,
		cellradius: 5,
		legend: legend_range,
		legendColors: [sensor_setup[sensor_name].color.replace(/\%,.*\%\)/gi, '%, 95%)'), sensor_setup[sensor_name].color]
	});
}


//-------------------------------------------------------------------------------
// Draws charts
//-------------------------------------------------------------------------------
function drawCharts(chart_names, drawDayNight, sensors) {

	// Clear chart area
	$('#graph-container').empty();

    // Override the reset function, we don't need to hide the tooltips and crosshairs.
    Highcharts.Pointer.prototype.reset = function () {
        return undefined;
    };


    // Synchronize zooming through the setExtremes event handler.
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

    var dayNightSeries = [];	
    if(drawDayNight == true){
		for(var i= 31; i >= 0; i--){
	    	var d = new Date();
	    	var times = SunCalc.getTimes(d.setDate(d.getDate() - i), 53.0128,-1.7325);
	    	dayNightSeries.push({
	                color: '#FCFFC5',
	                from: times.sunrise,
	                to: times.sunset
	            });
	    }
    }

	highchartOptions = {
        chart: {
            marginLeft: 60, // Keep all charts left aligned
            spacingTop: 10,
            spacingBottom: 10,
            zoomType: 'x'
        },
        title: {
            text: null, //sensors[sensor].description,
            align: 'left',
            margin: 0,
            x: 30
        },
        xAxis: {
            events: {
                setExtremes: syncExtremes
            },
        	type: 'datetime',
        	plotBands: dayNightSeries
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: false
        },
        tooltip: {
            shared: true,
            useHTML: true,
            crosshairs: true
        }
    }

    //Create a chart per unit type
    for (chart_no = 0; chart_no < chart_names.length; chart_no++) { 

    	//Populate each graph
    	var	valueSeries = [];		
		for (var sensor in sensors) {			

			//Add data with same units to same graph	
			if(sensors[sensor].chart_no === chart_no) {
				valueSeries.push({
	                data: sensors[sensor].readings,
	                step: sensors[sensor].step,
	                name: sensors[sensor].description,
	                type: sensors[sensor].graph,
	                color: sensors[sensor].color, ///Highcharts.getOptions().colors[sensors[sensor].color],
	                fillOpacity: 0.3,
	                marker: sensors[sensor].marker,
	                lineWidth: sensors[sensor].lineWidth,
	                tooltip: {
	                    valueSuffix: ' ' + sensors[sensor].unit,
	                    valueDecimals: sensors[sensor].decimals
	            	}
	            });
	        }
		}

		if(chart_names[chart_no].search('°C') !== -1) {
			highchartOptions.yAxis = {
				plotBands: [
					{ // Cold
			            from: -20,
			            to: 0,
			            color: 'rgba(68, 170, 213, 0.1)',
			            label: {
			                text: 'Cold',
			                style: {
			                    color: '#606060'
			                }
			            }
			        }, { // Hot
			            from: 35,
			            to: 100,
			            color: 'rgba(255, 50, 50, 0.1)',
			            label: {
			                text: 'Hot',
			                style: {
			                    color: '#606060'
			                }
			            }
			        }
			    ],
            	title: {
						text: chart_names[chart_no] //+ ' (' + units[i] + ')' 
				}
			}
		} else {
			// Add chart titles
			highchartOptions.yAxis = {
				opposite: sensors[sensor].opposite,
				title: {
					text: chart_names[chart_no] //+ ' (' + units[i] + ')' 
				}
			}
		}


		// Add data values
		highchartOptions.series = valueSeries;

		//console.log(highchartOptions);

		// Create chart
    	$('<div class="chart" style="height:180px">').appendTo('#graph-container').highcharts(highchartOptions);
	}

}

//-------------------------------------------------------------------------------
// Prepares yearly data and charts
//-------------------------------------------------------------------------------
function prepareYearCharts(chart_names, values) {

	var sensors = cloneObject(sensor_setup);

	// 1 year has a different chart layout
	sensors['inside_temp'].chart_no = 1;
	sensors['inside_hum'].chart_no = 2;
	sensors['precip_rate'].chart_no = 3;
	sensors['precip_acc'].chart_no = 3;
	sensors['door_open'].chart_no = null;
	sensors['sw_status'].chart_no = null;
	sensors['sw_power'].chart_no = 4;

	// Grab max min data
	// values = xmlGetData(dir + "_data/" + dataFiles['max']);
	// values_min = xmlGetData(dir + "_data/" + dataFiles['min']);

	// sensors = xmlGetDataInArray(dir + "_data/" + dataFiles['1y'] , sensors);

	// Append max min data 
	for(var sensor in sensors) {

		sensors[sensor].readings = values[sensor]; 

		if((sensor !== 'precip_acc') && (sensor !== 'precip_rate')){
		
			sensors[sensor + '_min_max'] = cloneObject(sensors[sensor]);

			sensors[sensor + '_min_max'].readings = []; 
			sensors[sensor + '_min_max'].description = 'Range';
			sensors[sensor + '_min_max'].graph = 'areasplinerange';
			sensors[sensor + '_min_max'].lineWidth = 0;
			sensors[sensor + '_min_max'].fillOpacity = 0.1;

			for(var j = 0; j < values[sensor + '_min'].length; j++) {
				values[sensor + '_min'][j].push(values[sensor + '_max'][j][1]);
			}				

			sensors[sensor + '_min_max'].readings = values[sensor + '_min']; 

		}

	}

	// Sensors below only show max values
	sensors['precip_rate'].description = 'Max precipitation rate';
	sensors['precip_acc'].description = 'Max accumulated precipitation';
	sensors['precip_rate'].readings = values['precip_rate_max'];
	sensors['precip_acc'].readings = values['precip_acc_max'];

	drawCharts(chart_names, false, sensors);
}

//-------------------------------------------------------------------------------
// Prepares data and displays it in a chart
//-------------------------------------------------------------------------------
function displayCharts(file_ref) {

	var chart_names;
	var dayNightList = ['1d', '2d', '1w', '1m'];
	var displayDayNight = (dayNightList.indexOf(file_ref) !== -1) ? true : false;

	// Highlights correct navbar location
	$('li').removeClass('active');
	$('#' + file_ref).parent().addClass('active');

	// Display charts
	if(file_ref === '1y') {
		chart_names = ['Outside Temp (°C)', 'Inside Temp (°C)', 'Humidity (%)', 'Rainfall (mm)', 'Switch Power (W)'];

		//Gets max data, then min data, then displayYearCharts
		xmlGetData(dir + '_data/' + dataFiles[file_ref], '', prepareYearCharts, [chart_names]);
	} else {
		chart_names = ['Temperature (°C)', 'Humidity (%)', 'Rainfall (mm)', 'Heater Status', 'Door Open'];
		xmlGetData(dir + '_data/' + dataFiles[file_ref], sensor_setup, drawCharts, [chart_names, displayDayNight]);
	}
}


//-------------------------------------------------------------------------------
// Prepares data and displays it on web load
//-------------------------------------------------------------------------------
function main() {

	formatAllDropdown(sensor_setup);

	xmlGetData(dir + '_data/' + dataFiles['1d'], sensor_setup, sidebarData, []);

	displayCharts('1d');

}



//===============================================================================
// Constants
//===============================================================================
var 	COLOR_BLUE		= 'hsl(198, 95%, 40%)', 	//'#058DC7',
 		COLOR_L_BLUE	= 'hsl(188, 79%, 52%)',		//'#24CBE5',
		COLOR_GREEN 	= 'hsl(106, 57%, 45%)',		//'#50B432',
		COLOR_L_GREEN 	= 'hsl(127, 71%, 65%)',		//'#64E572',
		COLOR_D_GREEN	= 'hsl(120, 100%, 20%)',	//'#006600',
		COLOR_ORANGE	= 'hsl(23, 100%, 67%)',		//'#FF9655',
		COLOR_PURPLE	= 'hsl(285, 100%, 40%)',	//'#9900cc',
		COLOR_PINK		= 'hsl(340, 100%, 70%)',	//'#ff6699',
		COLOR_YELLOW	= 'hsl(61, 100%, 44%)',		//'#DDDF00',
		COLOR_RED		= 'hsl(17, 85%, 52%)',		//'#ED561B',
		COLOR_ACQUA		= 'hsl(158, 92%, 70%)',		//'#6AF9C4',
		COLOR_BLACK		= 'hsl(0, 0%, 0%)',			//'#000000',
		COLOR_L_GREY	= 'hsl(0, 0%, 70%)',		//'#b3b3b3',
		COLOR_D_GREY	= 'hsl(0, 0%, 30%)';		//'#4d4d4d';



//===============================================================================
// Set up
//===============================================================================
var dir = 'weather',
	dataFiles = {'1d': 'wd_last_1d.xml',
				 '2d': 'wd_avg_2d.xml',
				 '1w': 'wd_avg_1w.xml',
				 '1m': 'wd_avg_1m.xml',
				 '3m': 'wd_avg_3m.xml',
				 '1y': 'wd_all_1y.xml'
			    },
	sensor_setup = { 'outside_temp': {
					description: 'Outside Temperature',
					chart_no: 0,
					unit: '°C',
					graph: 'spline',
					step: null,
					color: COLOR_BLUE,
					decimals: 2,
					opposite: false,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					fillOpacity: 0.75,
					readings: []
				},
				'inside_temp': {
					description: 'Inside Temperature',
					chart_no: 0,
					unit: '°C',
					graph: 'spline',
					step: null,
					color: COLOR_RED,
					decimals: 2,
					opposite: false,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					fillOpacity: 0.75,
					readings: []
				},
				'inside_hum': {
					description: 'Inside Humidity',
					chart_no: 1,
					unit: '%',
					graph: 'spline',
					step: null,
					color: COLOR_GREEN,
					decimals: 2,
					opposite: false,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					fillOpacity: 0.75,
					readings: []
				},
				'precip_rate': {
					description: 'Precipitation Rate',
					chart_no: 2,
					unit: 'mm',
					graph: 'line',
					step: 'center',
					color: COLOR_L_BLUE,
					decimals: 3,
					opposite: false,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					fillOpacity: 0.75,
					readings: []
				},
				'precip_acc': {
					description: 'Accumulated Precipitation',
					chart_no: 2,
					unit: 'mm',
					graph: 'spline',
					step: 'center',
					color: COLOR_ORANGE,
					decimals: 3,
					opposite: false,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					fillOpacity: 0.75,
					readings: []
				},
				'door_open': {
					description: 'Door Status',
					chart_no: 4,
					unit: '',
					graph: 'line',
					step: 'center',
					color: COLOR_PINK,
					decimals: 0,
					opposite: false,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					fillOpacity: 0.75,
					readings: []
				},
				'sw_status': {
					description: 'Switch Status',
					chart_no: 3,
					unit: '',
					graph: 'line',
					step: 'center',
					color: COLOR_YELLOW,
					decimals: 0,
					opposite: true,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					fillOpacity: 0.75,
					readings: []
				},
				'sw_power': {
					description: 'Switch Power',
					chart_no: 3,
					unit: 'W',
					graph: 'spline',
					step: null,
					color: COLOR_D_GREEN,
					decimals: 3,
					opposite: false,
					marker: {
						enable: true,
						radius: 1,
						symbol: 'circle'
					},
					lineWidth: 2,
					readings: []
				}
			};


//===============================================================================
// Run on load
//===============================================================================
main();

