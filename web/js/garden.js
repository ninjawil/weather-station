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


    getFileData('weather_data/gardening.json', 'json', drawGardenSearchBar, []);

}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenSearchBar(garden_data) {

	var HTMLPlantFilter = '<div id="bar1" class="col-md-4">%bar1%</div><div id="bar2" class="col-md-4">%bar2%</div><div id="bar3" class="col-md-2">%bar3%</div><div id="bar4" class="col-md-1">%bar4%</div><div id="bar5" class="col-md-1" style="top: 25px;;">%bar5%</div>',
		HTMLplantList = '<form><div class="form-group"><label for="plant_sel">Plant:</label><select multiple class="form-control" id="plant_sel"><option selected>All</option><option>%plant_list%</option></select><br></div></form>',
		HTMLlocList = '<form><div class="form-group"><label for="loc_sel">Location:</label><select multiple class="form-control" id="loc_sel"><option selected>All</option><option>%loc_list%</option></select><br></div></form>',
		HTMLdateList = '<form><div class="form-group"><label for="date_sel">Year:</label><select multiple class="form-control" id="date_sel"><option selected>All</option><option>%date_list%</option></select><br></div></form>',
		HTMLoptionsList = '<form><div class="form-group"><label for="options_sel">Options:</label><div class="checkbox"><label><input type="checkbox" value="" checked="checked" id="alive_check">Alive</label></div><div class="checkbox"><label><input type="checkbox" value="" id="watering_check">Watering</label></div></div></form>',
		HTMLfilterButton = '<button type="button" class="btn btn-secondary" id="filter-btn"><span class="glyphicon glyphicon-filter"></span></button>';


	// Prepare plant list
   	var plants_by_name = {};
   	for(var key in garden_data.plant_tags) {
   		plants_by_name[garden_data.plant_tags[key]] = key;
	}
    var plants = Object.keys(plants_by_name).sort();

	// Prepare location list
   	var locations_by_name = {};
   	for(var key in garden_data.location_tags) {
   		locations_by_name[garden_data.location_tags[key]] = key;
  	}
    var locations = Object.keys(locations_by_name).sort();

	// Prepare date list
   	var year_list = [];
    for (var note in garden_data.notes) {
    	var year = new Date(Number(garden_data.notes[note]['created'])).getFullYear().toString();
    	if ($.inArray(year, year_list) == -1) {
     		year_list.push(year);
    	}
    }

	// Draw filter options
	var f_HTMLPlantFilter 	=   HTMLPlantFilter.replace('%bar1%', HTMLplantList.replace("%plant_list%", plants.join('</option><option>')));
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar2%', HTMLlocList.replace("%loc_list%", locations.join('</option><option>')));
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar3%', HTMLdateList.replace("%date_list%", year_list.join('</option><option>')));
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar4%', HTMLoptionsList)
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar5%', HTMLfilterButton)

	$('#garden-input-bar-section').empty();
	$(f_HTMLPlantFilter).appendTo('#garden-input-bar-section');

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
			search_data.plant = Object.keys(garden_data.plant_tags); 
		} else {
			for (var i=0, len=plant_input.length; i<len; i++) {
				search_data.plant.push(plants_by_name[plant_input[i]]);
			}
		}

		// Return location guid
		var location_input = $( "#loc_sel" ).val();
		if($.inArray('All', location_input) !== -1) {
			search_data.location = Object.keys(garden_data.location_tags); 
		} else {
			for (var i=0, len=location_input.length; i<len; i++) {
				search_data.location.push(locations_by_name[location_input[i]]);
			}
		}

		if(search_data.year == 'All') {
			search_data.year = year_list; 
		}

        var sorted_data = sortGardenData(garden_data, search_data);

        getFileData('weather_data/state_tags.json', 'json', drawGardenChart, [sorted_data, garden_data]);



    }); 

}



//-------------------------------------------------------------------------------
// Sorts garden data
//-------------------------------------------------------------------------------
function sortGardenData(garden_data, search) {

	console.time("sort_data");

    // Filter notes
    var notes_sorted = {};
    for (var note in garden_data.notes) {
 
    	var date = new Date(Number(garden_data.notes[note].created));
    	var year = date.getFullYear().toString();
		var week = date.getWeek();

		var note_tags = garden_data.notes[note].tags;

    	if ($.inArray(year, search.year) !== -1) {

		    for (var i=0, i_len=search.plant.length; i<i_len; i++) {

			    if ($.inArray(search.plant[i], note_tags) !== -1) {	  

		    		// Create object if does not exist
					if ($.inArray(search.plant[i], Object.keys(notes_sorted)) === -1) {
						notes_sorted[search.plant[i]] = {};
					    notes_sorted[search.plant[i]][year] = [ 
					    	[], [], [], [], [], [], [], [], [], [],
					    	[], [], [], [], [], [], [], [], [], [],
					    	[], [], [], [], [], [], [], [], [], [],
					    	[], [], [], [], [], [], [], [], [], [],
					    	[], [], [], [], [], [], [], [], [], [],
					    	[], [], [], []
					    ];
					}

			    	notes_sorted[search.plant[i]][year][week].push(note);
			    }
			}
	    }	
    }


	console.timeEnd("sort_data");
	console.log(notes_sorted);

	return notes_sorted;

}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenChart(notes_to_display, garden_data, state) {
	    
	//var watering_tag = "cfdf9e45-d107-40fa-8852-e15c86a14202";
	//var dead_tag 	 = "9da9be98-9bf5-4170-9d8c-2a1751d11203";

	var HTMLtable = '<div class="table-responsive"><table class="table table-condensed"><thead><tr><th>Plant Name</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table></div>';
	var HTML_cell = "<td %cell_colour% nowrap><div style='cursor:pointer' data-toggle='popover' data-placement='auto' data-html='true' title='<b>%popover_title%</b>' data-content='<dl>%popover_body%</dl>'>%plant_symbol%</div>";
	var HTML_popover_img = '<img src="%res_link%" width="200" />';
	var HTML_popover_link = '<dd><a href="%url%">• %link_text%</a></dd>';

	var state_tags = Object.keys(state);

	var today = new Date();
	today_wk = today.getWeek(); // align to week 0
	today_yr = today.getFullYear().toString();


	// Filter tags
	for(var key in state) {
    	if(state[key] === '*watering') {
    		var watering_tag = key;
    		break;
	    }
	}

	for(var key in state) {
    	if(state[key] === '*dead') {
    		var dead_tag = key;
    		break;
	    }
	}

	if (!$('#watering_check').is(':checked')) {
		delete state[watering_tag];
	}

	// Create week number table header
	var week_numbers = [];
	for (i = 0; i < 54; i++) {
		week_numbers.push('00'.substring(i.toString().length) + i.toString());
	}
	var HTML_header_week_no = '<th>' + week_numbers.join('</th><th>') + '</th>';

	var HTML_row = [];
	for (var plant in notes_to_display) {

		HTML_row.push('<tr><td nowrap>' + garden_data.plant_tags[plant] + '</td>');

		for (var year in notes_to_display[plant]) {
			
			// Reset variables
			var cell_colour = '',
				popover_img = '',
				plant_dead  = false;

			HTML_row.push('<td>' + year + '</td>');

			// Loop through each week
			for (var week=0, week_len=notes_to_display[plant][year].length; week<week_len; week++) {

				var note = notes_to_display[plant][year][week];

				var formatted_HTML_cell = '<td %cell_colour%></td>';

				// Clear cell contents for future weeks
				if((week > today_wk && year === today_yr) || plant_dead ){
						formatted_HTML_cell = '<td></td>';

				} else if (note.length > 0) {

					var cell_symbols 	= '',
						popover_title 	= '',
						popover_body 	= '';

					if (cell_colour === ''){
						cell_colour = 'class="success"';
					}

					// Loop through all notes in the week
					for (var i=0, note_len=note.length; i<note_len; i++) {
						for (var tag=0, tag_len=garden_data.notes[note[i]].tags.length; tag<tag_len; tag++) {

							var state_tag = garden_data.notes[note[i]].tags[tag];

							if ( $.inArray(state_tag, state_tags) !== -1 ) {

								// Set cell color depending on plant state
								if( state[state_tag].color !== '' ) {
									cell_colour = 'class="' + state[state_tag].color + '"';
								}

								// Populate symbols for cell
								cell_symbols = cell_symbols + state[state_tag].symbol;

								// Add image if present in note
								if(garden_data.notes[note[i]].res.length > 0) {
									popover_img = HTML_popover_img.replace('%res_link%', garden_data.notes[note[i]].res[0]);								
								}

								// Stop shading cells if plant has died
								if ( state_tag === dead_tag ) {
									plant_dead = true;
								}
							}							
						}

						// Create popover or append if multiple notes in a single week
						popover_title = popover_title !== '' ? 'Multiple notes this week' : garden_data.notes[note[i]].title;
						popover_body  = popover_body + HTML_popover_link.replace('%url%', garden_data.notes[note[i]].link);
						popover_body  = popover_body.replace('%link_text%', garden_data.notes[note[i]].title);

					}
	
					// Create popover			
					formatted_HTML_cell = HTML_cell.replace('%popover_title%', popover_title);
					formatted_HTML_cell = formatted_HTML_cell.replace('%popover_body%', popover_body + popover_img);
					
					// Draw cell
					formatted_HTML_cell = formatted_HTML_cell.replace('%plant_symbol%', cell_symbols);

				}

				formatted_HTML_cell = formatted_HTML_cell.replace('%cell_colour%',  cell_colour);
				HTML_row.push(formatted_HTML_cell);
			}	
		}

		// Draw row
		HTML_row.push('</tr>');
	}

	// Clear chart area
	$('#chart-section').empty();

	// Draw table
    formattedHTMLtable = HTMLtable.replace("%week_no%", HTML_header_week_no);
    formattedHTMLtable = formattedHTMLtable.replace("%plants%", HTML_row.join(''));
	$('#chart-section').append(formattedHTMLtable);

	// Enable popover
	$(document).ready(function() {
	    $("#chart-section").popover({ selector: '[data-toggle=popover]' });
	});


}