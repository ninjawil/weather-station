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
    $('<div class="row"><div id="garden-input-bar-section" class="text-left"></div></div>').appendTo('#graph-container');
    $('<div class="row"><div id="chart-section"></div></div>').appendTo('#graph-container');


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
   	var plants_by_name = {};
   	for(var key in garden_data['plant_tags']) {
   		plants_by_name[garden_data['plant_tags'][key]] = key;
	}

    var plants = Object.keys(plants_by_name).sort();
 	
   	var plant_list =  "<option selected> All </option>";
    for (var i = 0; i <= plants.length - 1; i++) {
    	plant_list = plant_list + "<option>" + plants[i] + "</option>";
    }
    formattedHTMLplantList = HTMLplantList.replace("%plant_list%", plant_list);

	// Prepare location list
   	var locations_by_name = {};
   	for(var key in garden_data['location_tags']) {
   		locations_by_name[garden_data['location_tags'][key]] = key;
  	}
    var locations = Object.keys(locations_by_name).sort();

   	var loc_list = "<option selected> All </option>";
    for (var i = 0; i <= locations.length - 1; i++) {
    	loc_list = loc_list + "<option>" + locations[i] + "</option>";
    }
    formattedHTMLlocList = HTMLlocList.replace("%loc_list%", loc_list);

	// Prepare date list
   	var year_list = ['2015', '2016', '2017']; //[];
    // for (var note in garden_data['notes']) {
    // 	date = new Date(Number(garden_data['notes'][note]['created']));
    // 	if ($.inArray(date.getFullYear(), year_list)) {
    // 		year_list.push(date.getFullYear().toString());
    // 	}

    // }
   	var html_year_list = "<option selected> All </option>";
    for (var year in year_list) {
    	html_year_list = html_year_list + "<option>" + year_list[year] + "</option>";
    }
    formattedHTMLdateList = HTMLdateList.replace("%date_list%", html_year_list);


	$('#bar1').append(formattedHTMLplantList);
	$('#bar2').append(formattedHTMLlocList);
	$('#bar3').append(formattedHTMLdateList);
	$('#bar4').append(HTMLaliveList);
	$('#bar5').append(HTMLfilterButton);

	$("#filter-btn").click(function(){

		search_data = {
			"plant": 	[],
			"location": [],
			"year": 	$( "#date_sel" ).val(),
			"alive": 	$( "#alive_sel" ).val()
		}

		// Return plant guid
		var plant_input = $( "#plant_sel" ).val();
		if($.inArray('All', plant_input) !== -1) {
			search_data['plant'] = Object.keys(garden_data['plant_tags']); 
		} else {
			for (var i = 0; i <= plant_input.length - 1; i++) {
				search_data["plant"].push(plants_by_name[plant_input[i]]);
			}
		}

		// Return location guid
		var location_input = $( "#loc_sel" ).val();
		if($.inArray('All', location_input) !== -1) {
			search_data['location'] = Object.keys(garden_data['location_tags']); 
		} else {
			for (var i = 0; i <= location_input.length - 1; i++) {
				search_data["location"].push(locations_by_name[location_input[i]]);
			}
		}

		if(search_data['year'] == 'All') {
			search_data['year'] = year_list; 
		}

        drawGardenChart(sortGardenData(garden_data, search_data), garden_data);
    }); 

}



//-------------------------------------------------------------------------------
// Sorts garden data
//-------------------------------------------------------------------------------
function sortGardenData(garden_data, search) {

	console.log(search);

	var filtered_data = {};

    // Filter notes 1st by date, 2nd by Plant name and 3rd by location
    var notes_flt = [];
    for (var note in garden_data['notes']) {
 
    	var date = new Date(Number(garden_data['notes'][note]['created']));

    	if ($.inArray(date.getFullYear().toString(), search['year']) !== -1) {
    		if(	containsSome(search['plant'], garden_data['notes'][note]['tags']) &&
    			containsSome(search['location'], garden_data['notes'][note]['tags'])) {

				notes_flt.push(note);			
			}
	    }	
    }

    // Sort notes into plant and location order
    var notes_sorted = {};
	for (var k = 0; k <= notes_flt.length - 1; k++) {
    
	    for (var i = 0; i <= search['plant'].length - 1; i++) {
		    if ($.inArray(search['plant'][i], garden_data['notes'][notes_flt[k]]['tags']) !== -1) {	  

		    	// Create a key if it does not exist
				if ($.inArray(search['plant'][i], Object.keys(notes_sorted)) === -1) {
				    notes_sorted[search['plant'][i]] = {};
				}
		      
			    for (var j = 0; j <= search['location'].length - 1; j++) {	    	
			    	if ($.inArray(search['location'][j], garden_data['notes'][notes_flt[k]]['tags']) !== -1) {

			    		var year = new Date(Number(garden_data['notes'][notes_flt[k]]['created'])).getFullYear().toString();

		    			// Create a key if it does not exist
				    	if ($.inArray(search['location'][j], Object.keys(notes_sorted[search['plant'][i]])) === -1) {
				    		notes_sorted[search['plant'][i]][search['location'][j]] = {};
					    	notes_sorted[search['plant'][i]][search['location'][j]][year] = [];
			    		} else {
					    	if ($.inArray(year, Object.keys(notes_sorted[search['plant'][i]][search['location'][j]])) === -1) {
					    		notes_sorted[search['plant'][i]][search['location'][j]][year] = [];
				    		}
				    	}

				    	notes_sorted[search['plant'][i]][search['location'][j]][year].push(notes_flt[k]);
			    	}
			    }
		    }
		}
	}

	return notes_sorted;

}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenChart(notes_to_display, garden_data) {

	// Clear chart area
	$('#chart-section').empty();

	console.log(notes_to_display);

	HTMLtable = '<div class="table-responsive"><table class="table table-condensed"><thead><tr><th>Plant Name</th><th>Location</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table></div>';

	var HTML_title_week_no = '';
	var HTML_week_no = '';
	for (i = 0; i < 54; i++) {
		HTML_title_week_no = HTML_title_week_no + '<th>' + '00'.substring(i.toString().length) + i.toString() + '</th>';
		HTML_week_no = HTML_week_no + '<th>%wk' + i.toString() + '%</th>';
	}

	var HTML_plants = '<tr>';
	for (var plant in notes_to_display) {
		for (var location in notes_to_display[plant]) {
			for (var year in notes_to_display[plant][location]) {
				
				HTML_plants = HTML_plants + '<td>' + garden_data['plant_tags'][plant] + '</td>';
				HTML_plants = HTML_plants + '<td>' + garden_data['location_tags'][location] + '</td>';
				HTML_plants = HTML_plants + '<td>' + year + '</td>';

				formatted_HTML_week_no = HTML_week_no;
				
				for (var i = 0; i <= notes_to_display[plant][location][year].length - 1; i++) {

					var date = new Date(Number(garden_data['notes'][notes_to_display[plant][location][year][i]]['created']));

					console.log(date);
					console.log(date.getWeek());

					formatted_HTML_week_no = formatted_HTML_week_no.replace('%wk' + date.getWeek().toString() + '%', 'XX');
				}

    			HTML_plants = HTML_plants + formatted_HTML_week_no + '</tr>';	
			}
		}	
	}


    formattedHTMLtable = HTMLtable.replace("%week_no%", HTML_title_week_no);
    formattedHTMLtable = formattedHTMLtable.replace("%plants%", HTML_plants);
    formattedHTMLtable = formattedHTMLtable.replace(/%wk\d+%/g, '');

	$('#chart-section').append(formattedHTMLtable);


}