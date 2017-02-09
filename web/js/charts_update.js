//
// charts_update.js
// Will De Freitas
//
// Draws charts based on xml files
//
// 

//-------------------------------------------------------------------------------
// Converts time since last epoch and displays it on the webpage
//-------------------------------------------------------------------------------
function displayTime(timeSinceEpoch) {

	var HTMLupdateTime = '<div class="row">%time%</div><div class="row">%date%</div>';

	//Convert time since epoch to human dates (time needs to be in milliseconds)
	var datetime = new Date(timeSinceEpoch);
	var time 	 = datetime.toLocaleTimeString();

	if(datetime.getTimezoneOffset() == "-60") {
		time += " &#x263C;";
	}

	var f_HTMLupdateTime =   HTMLupdateTime.replace("%time%", time)
	f_HTMLupdateTime 	 = f_HTMLupdateTime.replace("%date%", datetime.toUTCString().slice(0, 17));

	//Display time and date
	$('#update_time').append(f_HTMLupdateTime);	
}


//-------------------------------------------------------------------------------
// Displays last updated values on web page
//-------------------------------------------------------------------------------
function sidebarData(sensors) {

	
	var HTMLvalueBox = '<div id="%id%" class="row reading-group"><div class="row reading-value">%value%<span class="reading-unit"> %unit%</span></div><div class="row reading-name">%description%</div></div>';
	//var HTMLvalue = '<div class="row reading-value">%value%<span class="reading-unit"> %unit%</span></div>';

	var f_HTMLvalueBox = '',
		f_HTMLvalue    = '';

	for(var sensor in sensors) {

		f_HTMLvalueBox = HTMLvalueBox.replace("%id%", sensor);
		f_HTMLvalueBox = f_HTMLvalueBox.replace("%description%", sensors[sensor].description);

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

			f_HTMLvalueBox = f_HTMLvalueBox.replace("%value%", value);
			f_HTMLvalueBox = f_HTMLvalueBox.replace("%unit%", sensors[sensor].unit);


		}
		
		f_HTMLvalue += f_HTMLvalueBox;
	}

	//Display data
	$("#sidebar").append(f_HTMLvalue);		
		// $('#' + sensor).prepend(f_HTMLvalue);

	// Display last update time
	displayTime(sensors['door_open'].readings[sensors['door_open'].readings.length-1][0]);
}


//-------------------------------------------------------------------------------
// Displays last updated values on web page
//-------------------------------------------------------------------------------
function formatAllDropdown(sensors) {

	var HTMLallDropdown = '<li><a href="#" onclick="displayHeatMap(%id%)">%name%</a></li>';

	var f_Dropdown,
		f_Dropdown_list = [];

	for(var sensor in sensors) {
		if (!sensors.hasOwnProperty(sensor)) continue;

		f_Dropdown = HTMLallDropdown.replace("%id%", "'" + sensor + "'");
		f_Dropdown = f_Dropdown.replace("%name%", sensors[sensor].description);

		f_Dropdown_list.push(f_Dropdown);
	}

	//Display data		
	$('#allDropdown').append(f_Dropdown_list.join(''));
}



//-------------------------------------------------------------------------------
// Gets data from XML file
//-------------------------------------------------------------------------------
function xmlGetData(filename, sensors_array, functionCall, args) {

	var xhttp = new XMLHttpRequest();

	var output_data = {};

	xhttp.onreadystatechange = function() {
	    if (xhttp.readyState == 4) {
			if (xhttp.status == 200) {

				var xml = xhttp.responseXML,
					xml_sensors  = xml.getElementsByTagName("entry"),
					xmlValue = xml.getElementsByTagName("row");

				for(var i=0, i_len=xml_sensors.length; i<i_len; i++) {

					output_data[xml_sensors[i].childNodes[0].nodeValue] = [];

					for(var j=0, j_len=xmlValue.length; j<j_len; j++) {
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
			else{
				console.log("Error: ", xhttp.statusText);
			}
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
	var title = '<div id="title-section"><div class="row"><h4>%name%</h4></div><div id="cal-heatmap"></div></div><div id="charts-section"></div>';
    $(title.replace("%name%", sensor_setup[sensor_id].description)).appendTo('#graph-container');

	xmlGetData(dir + '_data/' + 'wd_all_2016.xml', '', drawHeatMap, ['2016', sensor_id]);
	xmlGetData(dir + '_data/' + 'wd_all_2017.xml', '', drawHeatMap, ['2017', sensor_id]);
    
}


//-------------------------------------------------------------------------------
// Draw heat map
//-------------------------------------------------------------------------------
function drawHeatMap(year, sensor_name, value_array) {

	var draw_row = '<div class="row"><div class="col-md-1"><div class="vertical-text"><h4>%year%</h4></div></div><div id="charts-col2-%year%" class="col-md-11"></div></div>'	

    $(draw_row.replace(/%year%/g, year)).appendTo('#graph-container');

    var parser = function(data) {
		var stats = {};
		for (var d in data) {
			stats[data[d][0]/1000] = data[d][1];
		}
		return stats;
	};

	var data_array = [];
	for(var i=0, len=value_array[sensor_name].length; i<len; i++){
		data_array.push(value_array[sensor_name][i][1]);
	}

	var min_of_array = Math.min.apply(Math, data_array);
	var max_of_array = Math.max.apply(Math, data_array);
	var legend_range = [0,0,0,0];

	// legend_range[3] = average(data_array) + standardDeviation(data_array);
	legend_range[3] = 0.75*max_of_array;
	legend_range[2] = min_of_array + 0.75*(legend_range[3] - min_of_array);
	legend_range[1] = min_of_array + 0.50*(legend_range[3] - min_of_array);
	legend_range[0] = min_of_array + 0.25*(legend_range[3] - min_of_array);

	var item = "#charts-col2-%year%".replace("%year%", year);


	var calendar = new CalHeatMap();
	calendar.init({
		itemSelector: item,
		data: value_array[sensor_name],
		afterLoadData: parser,
		itemName: [sensor_setup[sensor_name].unit, sensor_setup[sensor_name].unit],
		start: new Date(year, 0),
		domain : "month",			// Group data by month
		subDomain : "day",			// Split each month by days
		cellsize: 20,
		cellpadding: 3,
		cellradius: 5,
		tooltip: true,
		legendVerticalPosition: "center",
		legendHorizontalPosition: "right",
		legendOrientation: "vertical",
		legend: legend_range,
		legendColors: {
			min: 	sensor_setup[sensor_name].color.replace(/\%,.*\%\)/gi, '%, 85%)'), 
			max: 	sensor_setup[sensor_name].color,
			empty: 	sensor_setup[sensor_name].color.replace(/\%,.*\%\)/gi, '%, 95%)') //"#ededed"
		}
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
    for (chart_no=0, chart_len=chart_names.length; chart_no<chart_len; chart_no++) { 

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
	                zIndex: sensors[sensor].zIndex,
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
			sensors[sensor + '_min_max'].graph = 'arearange';
			sensors[sensor + '_min_max'].color = sensors[sensor + '_min_max'].color.replace(/\%,.*\%\)/gi, '%, 80%)');
			sensors[sensor + '_min_max'].zIndex = 0;
			sensors[sensor + '_min_max'].lineWidth = 2;
			sensors[sensor + '_min_max'].fillOpacity = 0.3;

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
	if(['1d', '2d', '1w', '1m', '3m'].indexOf(file_ref) == -1) {
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

	console.time('main');

	formatAllDropdown(sensor_setup);

	xmlGetData(dir + '_data/' + dataFiles['1d'], sensor_setup, sidebarData, []);

	displayCharts('1d');

	console.timeEnd('main');
}



//===============================================================================
// Constants
//===============================================================================
var 	COLOR_BLUE		= 'hsl(210, 95%, 40%)', 	//'#058DC7',
 		COLOR_L_BLUE	= 'hsl(188, 79%, 52%)',		//'#24CBE5',
		COLOR_GREEN 	= 'hsl(106, 57%, 45%)',		//'#50B432',
		COLOR_L_GREEN 	= 'hsl(127, 71%, 65%)',		//'#64E572',
		COLOR_D_GREEN	= 'hsl(120, 100%, 20%)',	//'#006600',
		COLOR_ORANGE	= 'hsl(23, 100%, 67%)',		//'#FF9655',
		COLOR_PURPLE	= 'hsl(285, 100%, 40%)',	//'#9900cc',
		COLOR_PINK		= 'hsl(340, 100%, 70%)',	//'#ff6699',
		COLOR_YELLOW	= 'hsl(61, 100%, 44%)',		//'#DDDF00',
		COLOR_RED		= 'hsl(5, 85%, 52%)',		//'#ED561B',
		COLOR_ACQUA		= 'hsl(158, 92%, 70%)',		//'#6AF9C4',
		COLOR_BLACK		= 'hsl(0, 0%, 0%)',			//'#000000',
		COLOR_L_GREY	= 'hsl(0, 0%, 70%)',		//'#b3b3b3',
		COLOR_D_GREY	= 'hsl(0, 0%, 30%)';		//'#4d4d4d';



//===============================================================================
// Set up
//===============================================================================
var d = new Date();
var n = d.getFullYear();
var dir = 'weather',
	dataFiles = {'1d': 'wd_last_1d.xml',
				 '2d': 'wd_avg_2d.xml',
				 '1w': 'wd_avg_1w.xml',
				 '1m': 'wd_avg_1m.xml',
				 '3m': 'wd_avg_3m.xml',
				 '1y': 'wd_all_'+ n + '.xml',
				 '2016': 'wd_all_2016.xml'
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
					readings: [],
					zIndex: 6
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
					readings: [],
					zIndex: 6
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
					readings: [],
					zIndex: 6
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
					readings: [],
					zIndex: 6
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
					readings: [],
					zIndex: 6
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
					readings: [],
					zIndex: 6
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
					readings: [],
					zIndex: 6
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
					readings: [],
					zIndex: 6
				}
			};


//===============================================================================
// Run on load
//===============================================================================
main();

