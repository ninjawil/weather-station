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
	$('<div id="bar1" class="col-md-4"></div><div id="bar2" class="col-md-4"></div><div id="bar3" class="col-md-2"></div><div id="bar4" class="col-md-1"></div><div id="bar5" class="col-md-1" style="top: 25px;;"></div>').appendTo('#garden-input-bar-section');

	HTMLplantList = '<form><div class="form-group"><label for="plant_sel">Plant:</label><select multiple class="form-control" id="plant_sel">%plant_list%</select><br></div></form>';
	HTMLlocList = '<form><div class="form-group"><label for="loc_sel">Location:</label><select multiple class="form-control" id="loc_sel">%loc_list%</select><br></div></form>';
	HTMLdateList = '<form><div class="form-group"><label for="date_sel">Year:</label><select multiple class="form-control" id="date_sel">%date_list%</select><br></div></form>';
	HTMLaliveList = '<form><div class="form-group"><label for="alive_sel">Alive:</label><select class="form-control" id="alive_sel"><option> Y </option><option> N </option></select><br></div></form>';
	HTMLfilterButton = '<button type="button" class="btn btn-secondary" id="filter-btn"><span class="glyphicon glyphicon-filter"></span></button>';

	// Prepare plant list
   	var plant_list =  "<option> All </option>";
    for (var plant in garden_data['plants']) {
    	plant_list = plant_list + "<option>" + plant + "</option>";
    }
    formattedHTMLplantList = HTMLplantList.replace("%plant_list%", plant_list);

	// Prepare location list
   	var loc_list = "<option> All </option>";
    for (var location in garden_data['location']) {
    	loc_list = loc_list + "<option>" + location + "</option>";
    }
    formattedHTMLlocList = HTMLlocList.replace("%loc_list%", loc_list);

	// Prepare date list
   	var year_list = [];
    for (var note in garden_data['notes']) {
    	date = new Date(Number(garden_data['notes'][note]['created']));
    	if ($.inArray(date.getFullYear(), year_list)) {
    		year_list.push(date.getFullYear());
    	}

    }
   	var html_year_list = "<option> All </option>";
    for (var year in year_list) {
    	html_year_list = html_year_list + "<option>" + year_list[year].toString() + "</option>";
    }
    formattedHTMLdateList = HTMLdateList.replace("%date_list%", html_year_list);


	$('#bar1').append(formattedHTMLplantList);
	$('#bar2').append(formattedHTMLlocList);
	$('#bar3').append(formattedHTMLdateList);
	$('#bar4').append(HTMLaliveList);
	$('#bar5').append(HTMLfilterButton);

	$("#filter-btn").click(function(){

		search_data = {
			"plant": 	$( "#plant_sel" ).val(),
			"location": $( "#loc_sel" ).val(),
			"year": 	$( "#date_sel" ).val(),
			"alive": 	$( "#alive_sel" ).val()
		}

		if(search_data['plant'] == 'All') {
			search_data['plant'] = Object.keys(garden_data['plants']); 
		}

		if(search_data['location'] == 'All') {
			search_data['location'] = Object.keys(garden_data['location']); 
		}

		if(search_data['year'] == 'All') {
			search_data['year'] = year_list; 
		}

        drawGardenChart(garden_data, search_data);
    }); 

	// drawGardenChart(garden_data, search);

}

//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenChart(garden_data, search) {

	// Clear chart area
	$('#chart-section').empty();

	console.log(search);

	var filtered_data = {};
	    

	for (var plant in search['plants']) { 
	    for (var note in garden_data['notes']) {
	    	if ($.inArray(garden_data['notes'][search['plants']], garden_data['notes'][note]['tags']) !== -1) {
    			filtered_data[plant].push(note);
	    	}
	    }
	}

	console.log(filtered_data);

    for (var note in garden_data['notes']) {
    	if ($.inArray(plant_tag_guid, garden_data['notes'][note]['tags']) !== -1 && 
    		$.inArray(location_tag_guid, garden_data['notes'][note]['tags']) !== -1) {
			
			date = new Date(Number(garden_data['notes'][note]['created']));

	    	if (date.getFullYear() == search['year'] ||	search['year'] == 'All') {
    			filtered_data.push(note);
	    	}
   		}
	}
  	


	console.log(filtered_data);

	HTMLtable = '<table class="table table-bordered"><thead><tr><th>Plant Name</th><th>Location</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table>';

	var week_no = '';
	for (i = 0; i < 54; i++) {
		week_no = week_no + '<th>' + i.toString() + '</th>';
	}

	var plants = '';
	for (var plant in search['plant']) {
		plants = plants + '<tr><td>' + search['plant'] + '</td><td>' + search['location'] + '</td><td>' + search['year'] + '</td>';

		plants = plants + '</tr>';		
	}


    formattedHTMLtable = HTMLtable.replace("%week_no%", week_no);
    formattedHTMLtable = formattedHTMLtable.replace("%plants%", plants);

	$('#chart-section').append(formattedHTMLtable);


}