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
    $('<div id="garden-input-bar-section" class="text-left"></div>').appendTo('#graph-container');
    $('<div id="chart-section"></div>').appendTo('#graph-container');


    getGardenData(drawGardenSearchBar, []);

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
            args.push(config_data);
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
function drawGardenSearchBar(garden_data) {

	// Clear chart area
	$('#garden-input-bar-section').empty();

	console.log(garden_data);

	HTMLplantList = '<form><div class="form-group"><label for="plant_sel">Select list (select one):</label><select class="form-control" id="plant_sel">%plant_list%</select><br></div></form>';

   	var plant_list =  "";

    for (var plant in garden_data['plants']) {
    	plant_list = plant_list + "<option>" + plant + "</option>";
    }

    console.log(plant_list);

    formattedHTMLplantList = HTMLplantList.replace("%plant_list%", plant_list);
	$('#garden-input-bar-section').append(formattedHTMLplantList);



}

//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenChart(garden_data) {

	// Clear chart area
	$('#chart-section').empty();

}