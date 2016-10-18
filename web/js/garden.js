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

	HTMLPlantSearchContainer = '<div id="bar1" class="col-md-4"></div><div id="bar2" class="col-md-4"></div><div id="bar3" class="col-md-2"></div><div id="bar4" class="col-md-1"></div><div id="bar5" class="col-md-1" style="top: 25px;;"></div>';
	HTMLplantList = '<form><div class="form-group"><label for="plant_sel">Plant:</label><select multiple class="form-control" id="plant_sel">%plant_list%</select><br></div></form>';
	HTMLlocList = '<form><div class="form-group"><label for="loc_sel">Location:</label><select multiple class="form-control" id="loc_sel">%loc_list%</select><br></div></form>';
	HTMLdateList = '<form><div class="form-group"><label for="date_sel">Year:</label><select multiple class="form-control" id="date_sel">%date_list%</select><br></div></form>';
	HTMLoptionsList = '<form><div class="form-group"><label for="options_sel">Options:</label><div class="checkbox"><label><input type="checkbox" value="" checked="checked" id="alive_check">Alive</label></div><div class="checkbox"><label><input type="checkbox" value="" id="watering_check">Watering</label></div></div></form>';
	// HTMLaliveList = '<form><div class="form-group"><label for="alive_sel">Alive:</label><select class="form-control" id="alive_sel"><option> Y </option><option> N </option></select><br></div></form>';
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
   	var year_list = [];
    for (var note in garden_data['notes']) {
    	var year = new Date(Number(garden_data['notes'][note]['created'])).getFullYear().toString();
    	if ($.inArray(year, year_list) == -1) {
     		year_list.push(year);
    	}
    }

   	var html_year_list = "<option selected> All </option>";
    for (var year in year_list) {
    	html_year_list = html_year_list + "<option>" + year_list[year] + "</option>";
    }
    formattedHTMLdateList = HTMLdateList.replace("%date_list%", html_year_list);


	// Clear chart area
	$('#garden-input-bar-section').empty();
	$(HTMLPlantSearchContainer).appendTo('#garden-input-bar-section');

	$('#bar1').append(formattedHTMLplantList);
	$('#bar2').append(formattedHTMLlocList);
	$('#bar3').append(formattedHTMLdateList);
	$('#bar4').append(HTMLoptionsList);
	$('#bar5').append(HTMLfilterButton);

	$("#filter-btn").click(function(){

		search_data = {
			"plant": 	[],
			"location": [],
			"year": 	$( "#date_sel" ).val(),
			"alive": 	$('#alive_check').is(':checked') ? "checked" : "unchecked",
			"watering": $('#watering_check').is(':checked') ? "checked" : "unchecked"
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

	    		var date = new Date(Number(garden_data['notes'][notes_flt[k]]['created']));
	    		var year = date.getFullYear().toString();
	    		var week = date.getWeek();
	    		week = '00'.substring(week.toString().length) + week.toString();

	    		// Create object if does not exist
				if ($.inArray(search['plant'][i], Object.keys(notes_sorted)) === -1) {
					notes_sorted[search['plant'][i]] = {}
				    notes_sorted[search['plant'][i]][year] = [ 
				    	[], [], [], [], [], [], [], [], [], [],
				    	[], [], [], [], [], [], [], [], [], [],
				    	[], [], [], [], [], [], [], [], [], [],
				    	[], [], [], [], [], [], [], [], [], [],
				    	[], [], [], [], [], [], [], [], [], [],
				    	[], [], [], []
				    ];


				}

		    	notes_sorted[search['plant'][i]][year][week].push(notes_flt[k]);
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

	// console.log(notes_to_display);

	var state_colours = {
	    "05760b67-5d9b-4c47-9b75-729c0f2f4614": "info",
	    "2fb9a7e6-99ac-487c-af7f-3c468ce31e95": "",
	    "6d2fab44-76fb-4f0a-b9b6-60846ebadba2": "success",
	    "6dc756b8-35fa-4136-8a7b-c826084b11ed": "danger",
	    "9da9be98-9bf5-4170-9d8c-2a1751d11203": "",
	    "a2a964fe-eb33-4fac-b2a9-2e001a8390e0": "",
	    "b6014f8c-a736-4672-97a5-77e6ae925a64": "success",
	    "cfdf9e45-d107-40fa-8852-e15c86a14202": "",	
    	"d3bd0212-af17-463d-b85d-01460c54b95c": ""
	  };

	var state_symbols = {
	    "05760b67-5d9b-4c47-9b75-729c0f2f4614": '<span class="ion-ios-flower" aria-hidden="true"></span>',
	    "2fb9a7e6-99ac-487c-af7f-3c468ce31e95": '<span class="glyphicon glyphicon-info-sign"></span>',
	    "6d2fab44-76fb-4f0a-b9b6-60846ebadba2": '£',
	    "6dc756b8-35fa-4136-8a7b-c826084b11ed": '<span class="ion-bug" aria-hidden="true"></span>',
	    "9da9be98-9bf5-4170-9d8c-2a1751d11203": "✝",
	    "a2a964fe-eb33-4fac-b2a9-2e001a8390e0": "X",
	    "b6014f8c-a736-4672-97a5-77e6ae925a64": '<span class="glyphicon glyphicon-grain"></span>',
	    "cfdf9e45-d107-40fa-8852-e15c86a14202": "⍵",
    	"d3bd0212-af17-463d-b85d-01460c54b95c": "m"
	  };

	var watering_tag = "cfdf9e45-d107-40fa-8852-e15c86a14202";
	var dead_tag 	 = "9da9be98-9bf5-4170-9d8c-2a1751d11203";

	var HTMLtable = '<div class="table-responsive"><table class="table table-condensed"><thead><tr><th>Plant Name</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table></div>';
	var HTML_cell = '<td class="%cell_colour%" nowrap><div style="cursor:pointer" data-toggle="popover" data-placement="auto" data-html="true" title="<b>%popover_title%</b>" data-content="%popover_body%">%plant_symbol%</div>';
	var HTML_popover_img = "<img src='%res_link%' width='200' />";
	var HTML_popover_link = "<a href='%url%'>%link_text%</a>";


	var today = new Date();
	today_wk = today.getWeek(); // align to week 0
	today_yr = today.getFullYear().toString();


	// Filter tags
	var state_tags = jQuery.extend({}, garden_data['state_tags']);
	if ($('#watering_check').is(':checked') === false) {
		delete state_tags[watering_tag];
	}


	var HTML_header_week_no = '';
	for (i = 0; i < 54; i++) {
		HTML_header_week_no = HTML_header_week_no + '<th>' + '00'.substring(i.toString().length) + i.toString() + '</th>';
	}

	var HTML_row = '<tr>';
	for (var plant in notes_to_display) {
		for (var year in notes_to_display[plant]) {
			
			var cell_colour = '',
				popover_img = '',
				plant_data  = '',
				plant_dead  = false;

			// Loop through each week
			for (var week = 0; week < notes_to_display[plant][year].length; week++) {

				var note = notes_to_display[plant][year][week];

				var formatted_HTML_cell = '<td class="%cell_colour%"></td>';

				// Clear cell contents for future weeks
				if((week > today_wk && year === today_yr) || plant_dead ){
						formatted_HTML_cell = '<td></td>';

				} else if (note.length > 0) {

					var cell_symbols 	= '',
						popover_title 	= '',
						popover_body 	= '';

					// Set max number of symbols to display per cell
					//var iter = note.length > 3 ? 3 : note.length;

					// Loop through all notes in the week
					for (var i = 0; i < note.length; i++) {

						// Get plant state
						var state_tag = containsSome(garden_data['notes'][note[i]]['tags'], Object.keys(state_tags));

						// Ignore if no state tag present
						if (state_tag !== false) {

							// Set cell color depending on plant state
							if( state_colours[state_tag] !== '' ) {
								cell_colour = state_colours[state_tag];
							}

							// Populate symbols for cell
							cell_symbols = cell_symbols + (state_tag ? state_symbols[state_tag] : '🛈');

							// Add image if present in note
							if(garden_data['notes'][note[i]]['res'].length > 0) {
								popover_img = HTML_popover_img.replace('%res_link%', garden_data['notes'][note[i]]['res'][0]);								
							}

							// Create popover or append if multiple notes in a single week
							popover_title = popover_title !== '' ? 'Multiple notes this week' : garden_data['notes'][note[i]]['title'];
							popover_body  = popover_body + HTML_popover_link.replace('%url%', garden_data['notes'][note[i]]['link']);
							popover_body  = popover_body.replace('%link_text%', garden_data['notes'][note[i]]['title']);

							// Stop shading cells if plant has died
							if ( state_tag === dead_tag ) {
								plant_dead = true;
							}

						}
					}
	
					// Create popover			
					formatted_HTML_cell = HTML_cell.replace('%popover_title%', popover_title);
					formatted_HTML_cell = formatted_HTML_cell.replace('%popover_body%', popover_body + popover_img);
					
					// Draw cell
					formatted_HTML_cell = formatted_HTML_cell.replace('%plant_symbol%', cell_symbols);
				}
				
				formatted_HTML_cell = formatted_HTML_cell.replace('%cell_colour%',  cell_colour);
				plant_data = plant_data + formatted_HTML_cell;
			}	
		}

		// Draw row
		HTML_row = HTML_row + '<td nowrap>' + garden_data['plant_tags'][plant] + '</td>';
		HTML_row = HTML_row + '<td>' + year + '</td>';
		HTML_row = HTML_row + plant_data + '</tr>';
	}

	// Draw table
    formattedHTMLtable = HTMLtable.replace("%week_no%", HTML_header_week_no);
    formattedHTMLtable = formattedHTMLtable.replace("%plants%", HTML_row);
	$('#chart-section').append(formattedHTMLtable);

	// Enable popover
	$(document).ready(function() {
	    $("#chart-section").popover({ selector: '[data-toggle=popover]' });
	});


}