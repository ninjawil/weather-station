//
// charts_update.js
// Will De Freitas
//
// Draws irrigation charts
//
// 


//-------------------------------------------------------------------------------
// Draws irrigation data 
//-------------------------------------------------------------------------------
function displayIrrigation() {
	// Highlights correct navbar location
	$('li').removeClass('active');
	$('#irrig').parent().addClass('active');

	// Clear chart area
	$('#graph-container').empty();


    getIrrigData(drawIrrigation, []);

}



//-------------------------------------------------------------------------------
// Grab irrigation data 
//-------------------------------------------------------------------------------
function getIrrigData(functionCall, args) {
	
    // $.getJSON('weather_data/irrigation.json', function(json) {
	//     drawIrrigation(json);
	// });
    
    $.ajax({
        cache: false,
        url: 'weather_data/config.json',
        dataType: "json",
        success: function(config_data) {
            $.ajax({
                cache: false,
                url: 'weather_data/irrigation.json',
                dataType: "json",
                success: function(chart_data) {
                    //drawIrrigation(config_data, chart_data);
                    args.push(config_data);
                    args.push(chart_data);
                    functionCall.apply(this, args);
                },
                error: function () {
                    console.log('loading irrigation file failure');
                },
                onFailure: function () {
                    console.log('loading irrigation file failure');
                }
            })
        }
    });
    
}



//-------------------------------------------------------------------------------
// Add irrigation amount
//-------------------------------------------------------------------------------
function addIrrigationAmount(amount, config_data, chart_data) {

    console.log(amount);
    console.log(config_data);
    console.log(chart_data.irrig_amount);

    chart_data.irrig_amount[0] = chart_data.irrig_amount[0] + amount * 10;

    if (chart_data.irrig_amount < 0) {
        chart_data.irrig_amount[0] = 0;
    } else if (chart_data.irrig_amount[0] > config_data.irrigation.IRRIG_FULL) {
        chart_data.irrig_amount[0] = config_data.irrigation.IRRIG_FULL;
    }

    console.log(chart_data.irrig_amount);

    saveIrrigation(chart_data);


}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawIrrigation(config_data, chart_data) {

	// Create chart
	var title = '<div class="row"><h1>%name%</h1></div><div id="irrig_title"></div>';
    // $(title.replace("%name%", 'irrigation')).appendTo('#graph-container');
    console.log(chart_data);
    console.log(config_data);


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

    dates = [];

    // Set up chart
	highchartOptions = {
        chart: {
            marginLeft: 60,
            spacingTop: 10,
            spacingBottom: 10,
            zoomType: 'x'
        },
        title: {
            text: null,
            align: 'left',
            margin: 0,
            x: 30
        },
        yAxis: [{ // Primary yAxis
            title: {
                text: 'Depth',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            min: 0,
            labels: {
                format: '{value} mm',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            }
        }, { // Secondary yAxis
            title: {
                text: 'Temperature',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            min: 0,
            labels: {
                format: '{value}°C',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            opposite: true
        }],
        xAxis: {
            events: {
                setExtremes: syncExtremes
            },
        	type: 'datetime',
            maxZoom: 48 * 3600 * 1000,
            crosshair: false
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: false
        },
        tooltip: {
            shared: false,
            useHTML: true,
            valueDecimals: 2,
            crosshairs: true
        },
        plotOptions: {
            area: {
                fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            },
            column: {
                stacking: 'normal'
            }
        },
        series: [
	        {            
	            name: 'Predicted Rainfall',
	            type: 'column',
	            data: chart_data.precip,
                pointStart: Date.UTC(chart_data.date[0], chart_data.date[1]-1, chart_data.date[2]),
                pointInterval: 24 * 3600 * 1000, // one day
	            color: COLOR_L_BLUE,
	            fillOpacity: 0.3,
	            tooltip: {
	                valueSuffix: 'mm'
	        	},
                stack: 'irrig'
	        },{
                name: 'Irrigation Amount',
                type: 'column',
                data: chart_data.irrig_amount,
                pointStart: Date.UTC(chart_data.date[0], chart_data.date[1]-1, chart_data.date[2]),
                pointInterval: 24 * 3600 * 1000, // one day
                color: COLOR_L_GREEN,
                fillOpacity: 0.3,
                tooltip: {
                    valueSuffix: 'mm'
                },
                stack: 'irrig'
            },{   
                name: 'Depth',
                type: 'area',
                data: chart_data.depth,
                pointStart: Date.UTC(chart_data.date[0], chart_data.date[1]-1, chart_data.date[2]),
                pointInterval: 24 * 3600 * 1000, // one day
                fillOpacity: 0.3,
                lineWidth: 4,
                color: COLOR_BLUE,
                tooltip: {
                    valueSuffix: 'mm'
                }
            },{
          //       name: 'Depth Linear',
          //       type: 'spline',
          //       data: chart_data.linear,
          //       //fillOpacity: 0.3,
          //       marker: {
          //           enabled: false
          //       },
          //       color: COLOR_L_GREY,
             //    dashstyle: 'dash',
             //    tooltip: {
             //        valueSuffix: 'mm'
                // }
            
            },{
	            name: 'Alarm Level',
	            type: 'line',
	            data: chart_data.alarm_level,
                pointStart: Date.UTC(chart_data.date[0], chart_data.date[1]-1, chart_data.date[2]),
                pointInterval: 24 * 3600 * 1000, // one day
	            color: COLOR_RED,
                dashstyle: 'dash',
	            fillOpacity: 0.3,
                marker: {
                    enabled: false
                },
	            tooltip: {
	                valueSuffix: 'mm'
	        	}
            },{
                name: 'Predicted Temp',
                type: 'spline',
                data: chart_data.temp,
                pointStart: Date.UTC(chart_data.date[0], chart_data.date[1]-1, chart_data.date[2]),
                pointInterval: 24 * 3600 * 1000, // one day
                fillOpacity: 0.3,
                color: COLOR_YELLOW,
                yAxis: 1,
                tooltip: {
                    valueSuffix: '°C'
                } 
	        }
        ]
    }

	// Draw chart
    $('<div class="chart" style="height:360px">').appendTo('#graph-container').highcharts(highchartOptions);

//     drawIrrigationBar(
    var irrig_amount = chart_data.irrig_amount[0];
    var irrig_depth_full = config_data.irrigation.IRRIG_FULL;

// }

// //-------------------------------------------------------------------------------
// // Draws irrigation bar
// //-------------------------------------------------------------------------------
// function drawIrrigationBar(irrig_amount, irrig_depth_full) {

    var HTMLirrigBar_edit   = HTMLirrigBar.replace(/%barvalue%/gi, (irrig_amount/irrig_depth_full)*100);
    HTMLirrigBar_edit       = HTMLirrigBar_edit.replace(/%irrig_amount%/gi, irrig_amount);
    HTMLirrigBar_edit       = HTMLirrigBar_edit.replace(/%irrig_depth_full%/gi, irrig_depth_full);
    var HTMLirrig_edit      = HTMLirrig.replace('%col1%', HTMLirrigButton);
    HTMLirrig_edit          = HTMLirrig_edit.replace('%col2%', HTMLirrigBar_edit);
    $(HTMLirrig_edit).appendTo('#graph-container');

}

//-------------------------------------------------------------------------------
// If user has irrigated, save it to json file
//-------------------------------------------------------------------------------
function saveIrrigation(form_data) {

    var json = JSON.stringify(form_data);
    var encoded = btoa(json);

    console.log('data saved');

    $.ajax({
        url: 'php/save_irrig_data.php',
        type: "post",
        data: 'json=' + encoded,
        success: function(rxData) {
            alert(rxData);
      }
    });

    displayIrrigation();


}


