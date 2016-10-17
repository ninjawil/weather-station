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

	// console.log(notes_to_display);

	var state_colours = {
	    "05760b67-5d9b-4c47-9b75-729c0f2f4614": "info",
	    "b6014f8c-a736-4672-97a5-77e6ae925a64": "success"
	  }

	var state_symbols = {
	    "05760b67-5d9b-4c47-9b75-729c0f2f4614": "♣",
	    "2fb9a7e6-99ac-487c-af7f-3c468ce31e95": "i",
	    "6d2fab44-76fb-4f0a-b9b6-60846ebadba2": "£",
	    "9da9be98-9bf5-4170-9d8c-2a1751d11203": "♱",
	    "a2a964fe-eb33-4fac-b2a9-2e001a8390e0": "X",
	    "b6014f8c-a736-4672-97a5-77e6ae925a64": "ϒ",
	    "cfdf9e45-d107-40fa-8852-e15c86a14202": "w"
	  }

	HTMLtable = '<div class="table-responsive"><table class="table table-condensed"><thead><tr><th>Plant Name</th><th>Location</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table></div>';
	HTML_symb_info = '<td class="%cell_colour%"><div style="cursor:pointer" data-toggle="popover" data-placement="top" data-html="true" title="<b>%popover_title%</b>" data-content="%popover_body%">%plant_symbol%</div></td>';
	HTML_popover_body = "<img src='%res_link%' width='200' />";


	var HTML_title_week_no = '';
	var HTML_week_no = '';
	for (i = 0; i < 54; i++) {
		HTML_title_week_no = HTML_title_week_no + '<th>' + '00'.substring(i.toString().length) + i.toString() + '</th>';
		HTML_week_no = HTML_week_no + '%wk' + i.toString() + '%';
	}

	var HTML_plants = '<tr>';
	for (var plant in notes_to_display) {
		for (var location in notes_to_display[plant]) {
			for (var year in notes_to_display[plant][location]) {
				
				HTML_plants = HTML_plants + '<td nowrap>' + garden_data['plant_tags'][plant] + '</td>';
				HTML_plants = HTML_plants + '<td>' + garden_data['location_tags'][location] + '</td>';
				HTML_plants = HTML_plants + '<td>' + year + '</td>';

				formatted_HTML_week_no = HTML_week_no;


				// Loop through each note
				//    - create the popover
				//    - assign a symbol depending on the state tag
				//    - assign the state colour
				//    - add note to relevant week number
				//    - 
				for (var i = 0; i <= notes_to_display[plant][location][year].length - 1; i++) {

					var note = notes_to_display[plant][location][year][i];
		
					// Create popover			
					formatted_HTML_symb_info = HTML_symb_info.replace('%popover_title%', garden_data['notes'][note]['title']);
					
					if(garden_data['notes'][note]['res'].length > 0){
						formatted_HTML_popover_body = HTML_popover_body.replace('%res_link%', garden_data['notes'][note]['res'][0]);
						formatted_HTML_symb_info = formatted_HTML_symb_info.replace('%popover_body%', formatted_HTML_popover_body);
					} else {
						formatted_HTML_symb_info = formatted_HTML_symb_info.replace('%popover_body%', '');
					}


					// Add plant state symbol
					var state_tag 	 = containsSome(garden_data['notes'][note]['tags'], Object.keys(garden_data['state_tags']));					

					formatted_HTML_symb_info = formatted_HTML_symb_info.replace('%plant_symbol%', state_tag ? state_symbols[state_tag] : 'i');
					formatted_HTML_symb_info = formatted_HTML_symb_info.replace('%cell_colour%',  state_tag ? state_colours[state_tag] : '');


					// Place symbol for note in week number column
					var date = new Date(Number(garden_data['notes'][note]['created']));

					formatted_HTML_week_no = formatted_HTML_week_no.replace('%wk' + date.getWeek().toString() + '%', formatted_HTML_symb_info);
				}

    			HTML_plants = HTML_plants + formatted_HTML_week_no + '</tr>';	
			}
		}	
	}


    formattedHTMLtable = HTMLtable.replace("%week_no%", HTML_title_week_no);
    formattedHTMLtable = formattedHTMLtable.replace("%plants%", HTML_plants);
    formattedHTMLtable = formattedHTMLtable.replace(/%wk\d+%/g, '<td></td>');

	$('#chart-section').append(formattedHTMLtable);

	$(document).ready(function() {
	    $("#chart-section").popover({ selector: '[data-toggle=popover]' });
	});


}