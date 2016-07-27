//
// charts_update.js
// Will De Freitas
//
// Draws irrigation charts
//
// 


//-------------------------------------------------------------------------------
// Grab irrigation data from 
//-------------------------------------------------------------------------------
function displayIrrigation() {
	// Highlights correct navbar location
	$('li').removeClass('active');
	$('#irrig').parent().addClass('active');

	// Clear chart area
	$('#graph-container').empty();

	// $.getJSON('weather_data/irrigation.json', function(json) {
	//     drawIrrigation(json);
	// });

    $.ajax({
        cache: false,
        url: 'weather_data/irrigation.json',
        dataType: "json",
        success: function(data) {
            drawIrrigation(data);
        }
    });
    
}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawIrrigation(chart_data) {

	// Create chart
	var title = '<div class="row"><h1>%name%</h1></div><div id="irrig_title"></div>';
    // $(title.replace("%name%", 'irrigation')).appendTo('#graph-container');
    console.log(chart_data);


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
    irrig_amount = [];

    // Create x axis values
    for(var i= 0; i < chart_data.depth.length; i++){ 
    	dates[i] = i;
        irrig_amount[i] = 0;
    }

    irrig_amount[0] = chart_data.irrig_amount;




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
        	categories: dates,
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
            }
        },
        series: [
	        {
	            name: 'Depth',
	            type: 'area',
	            data: chart_data.depth,
	            fillOpacity: 0.3,
	            lineWidth: 4,
	            color: COLOR_BLUE,
                tooltip: {
                    valueSuffix: 'mm'
                }
          //   },{
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
	            name: 'Predicted Temp',
	            type: 'spline',
	            data: chart_data.temp,
	            fillOpacity: 0.3,
	            color: COLOR_YELLOW,
	            yAxis: 1,
	            tooltip: {
	                valueSuffix: '°C'
	        	}
	        },{
	            name: 'Predicted Rainfall',
	            type: 'column',
	            data: chart_data.precip,
	            color: COLOR_L_BLUE,
	            fillOpacity: 0.3,
	            tooltip: {
	                valueSuffix: 'mm'
	        	}
	        },{
                name: 'Irrigation Amount',
                type: 'column',
                data: irrig_amount,
                color: COLOR_BLUE,
                fillOpacity: 0.3,
                tooltip: {
                    valueSuffix: 'mm'
                }
            },{
	            name: 'Alarm Level',
	            type: 'line',
	            data: chart_data.alarm_level,
	            color: COLOR_RED,
                dashstyle: 'dash',
	            fillOpacity: 0.3,
                marker: {
                    enabled: false
                },
	            tooltip: {
	                valueSuffix: 'mm'
	        	}
	        }
        ]
    }

	// Draw chart
    $(HTMLirrigButton).appendTo('#graph-container');
	$('<div class="chart" style="height:360px">').appendTo('#graph-container').highcharts(highchartOptions);

}



//-------------------------------------------------------------------------------
// If user has irrigated, save it to json file
//-------------------------------------------------------------------------------
function saveIrrigation() {

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

}


