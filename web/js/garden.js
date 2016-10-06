//
// garden.js
// Will De Freitas
//
// Draws garden charts
//
// 


//-------------------------------------------------------------------------------
// Draws garden data 
//-------------------------------------------------------------------------------
function displayGarden() {

	// Highlights correct navbar location
	$('li').removeClass('active');
	$('#garden').parent().addClass('active');

	// Clear chart area
	$('#graph-container').empty();

    // Set up chart screen sections
    $('<div id="garden-input-bar-section"></div>').appendTo('#graph-container');
    $('<div id="chart-section"></div>').appendTo('#graph-container');


    getGardenData(drawIrrigChart, []);

}


//-------------------------------------------------------------------------------
// Grab garden data 
//-------------------------------------------------------------------------------
function getGardenData(functionCall, args) {

    var error_data = {"9999": {"time":10, "msg": "Loading data failure"}};
	
    $.ajax({
        cache: false,
        url: 'weather_data/gardening.json',
        dataType: "json",
        success: function(config_data) {            
            args.push(chart_data);
            functionCall.apply(this, args);
        },
        error: function () {
            displayErrorMessage(error_data, false, false);
        },
        onFailure: function () {
            displayErrorMessage(error_data, false, false);
        }
    });
    
}



//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawIrrigChart(garden_data) {

	// Clear chart area
	$('#chart-section').empty();

}