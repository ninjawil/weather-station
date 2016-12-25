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


    //getFileData('weather_data/gardening.json', 'json', minimumSearchBar, []);
     getFileData('weather_data/gardening_web.json', 'json', drawGardenSearchBar, []);

}


//-------------------------------------------------------------------------------
// Draw garden search bar
//-------------------------------------------------------------------------------
function minimumSearchBar(garden_data) {


	// Prepare date list
   	var year_list = [];
    for (var note in garden_data.notes) {
    	var year = new Date(Number(garden_data.notes[note]['created'])).getFullYear().toString();
    	if ($.inArray(year, year_list) == -1) {
     		year_list.push(year);
    	}
    }

	var search_data = {
		"plant": 	Object.keys(garden_data.plant_tags),
		"location": Object.keys(garden_data.location_tags), 
		"year": 	year_list,
		"alive": 	"unchecked",
		"watering": "unchecked"
	}


    var sorted_data = sortGardenData(garden_data, search_data);

    getFileData('weather_data/state_tags.json', 'json', drawGardenChart, [sorted_data, garden_data]);


}


//-------------------------------------------------------------------------------
// Draw garden search bar
//-------------------------------------------------------------------------------
function drawGardenSearchBar(garden_data) {

	console.log(garden_data);
	console.time("search_bar");

	var HTMLPlantFilter = '<div id="bar1" class="col-md-4">%bar1%</div><div id="bar2" class="col-md-2">%bar2%</div><div id="bar3" class="col-md-1">%bar3%</div><div id="bar4" class="col-md-1" style="top: 25px;">%bar4%</div><div id="bar5" class="col-md-4"></div>',
		HTMLplantList = '<form><div class="form-group"><label for="plant_sel">Plant:</label><select multiple class="form-control" id="plant_sel"><option selected>All</option><option>%plant_list%</option></select><br></div></form>',
		HTMLlocList = '<form><div class="form-group"><label for="loc_sel">Location:</label><select multiple class="form-control" id="loc_sel"><option selected>All</option><option>%loc_list%</option></select><br></div></form>',
		HTMLdateList = '<form><div class="form-group"><label for="date_sel">Year:</label><select multiple class="form-control" id="date_sel"><option selected>All</option><option>%date_list%</option></select><br></div></form>',
		HTMLoptionsList = '<form><div class="form-group"><label for="options_sel">Options:</label><div class="checkbox"><label><input type="checkbox" value="" checked="checked" id="alive_check">Alive</label></div><div class="checkbox"><label><input type="checkbox" value="" id="watering_check">Watering</label></div></div></form>',
		HTMLfilterButton = '<button type="button" class="btn btn-secondary" id="filter-btn" style="margin-bottom: 10px"><span class="glyphicon glyphicon-filter"></span></button>';
		HTMLstateButton = '<button type="button" class="btn btn-secondary" id="state-btn"><span class="glyphicon glyphicon-th-list" data-toggle="modal" data-target="#modal_plant_state"></span></button>';


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
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar2%', HTMLdateList.replace("%date_list%", year_list.join('</option><option>')));
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar3%', HTMLoptionsList)
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar4%', HTMLfilterButton)

	$('#garden-input-bar-section').empty();
	$(f_HTMLPlantFilter).appendTo('#garden-input-bar-section');

	console.timeEnd("search_bar");

	$("#filter-btn").click(function(){

		var search_data = {
			"plant": 	$( "#plant_sel" ).val(),
			"location": 'All', //$( "#loc_sel" ).val(),
			"year": 	$( "#date_sel" ).val(),
			"alive": 	$('#alive_check').is(':checked') ? "checked" : "unchecked",
			"watering": $('#watering_check').is(':checked') ? "checked" : "unchecked"
		}

		// Return plant guid
		if($.inArray('All', search_data.plant) !== -1) {
			search_data.plant = Object.keys(garden_data.plant_tags); 
		} else {
			for (var i=0, len=search_data.plant.length; i<len; i++) {
				search_data.plant[i] = plants_by_name[search_data.plant[i]];
			}
		}

		// Return location guid
		if($.inArray('All', search_data.location) !== -1) {
			search_data.location = Object.keys(garden_data.location_tags); 
		} else {
			for (var i=0, len=search_data.location.length; i<len; i++) {
				search_data.location[i] = locations_by_name[search_data.location[i]];
			}
		}

		if($.inArray('All', search_data.year) !== -1) {
			search_data.year = year_list; 
		}

        //var sorted_data = sortGardenData(garden_data);

        //getFileData('weather_data/state_tags.json', 'json', drawGardenChart, [sorted_data, garden_data]);
        getFileData('weather_data/state_tags.json', 'json', sortGardenData, [garden_data]);

    }); 

}



//-------------------------------------------------------------------------------
// Sorts garden data
//-------------------------------------------------------------------------------
function sortGardenData(garden_data) {

	console.time("sort_data");

	var plant_tags = Object.keys(garden_data.plant_tags);
	var state_tags = Object.keys(garden_data.state_tags);
	var location_tags = Object.keys(garden_data.location_tags);
	var p_number_tags = Object.keys(garden_data.p_number_tags);

	for (var p in garden_data.p_number_tags) {
		if (garden_data.p_number_tags[p] === '+p01.00') {
			var first_p_no = p;
			break;
		}
	}


    // Filter notes
    var notes_sorted = {};
    for (var note in garden_data.notes) {
		if (!garden_data.notes.hasOwnProperty(note)) continue;

		var note_tags = garden_data.notes[note].tags;

		// Prepare note date 
    	var date = new Date(Number(garden_data.notes[note].created));
    	var year = date.getFullYear().toString();
		var week = date.getWeek();

		// If no plant number then make it +p01.00
		if(!containsAny(p_number_tags, note_tags)) note_tags.push(first_p_no);

	    // Find all tags for plant states
		var states = [],
			locations = [],
			plants = [];

	    for (var i=0, i_len=note_tags.length; i<i_len; i++) {
	    	if ($.inArray(note_tags[i], state_tags) !== -1) {
				states.push(note_tags[i]);
			} else if ($.inArray(note_tags[i], location_tags) !== -1) {
				locations.push(note_tags[i]);
			} else if ($.inArray(note_tags[i], plant_tags) !== -1) {
				plants.push(note_tags[i]);
			}
		}

		// Find all plant tags and create a record
	    for (var i=0, i_len=plants.length; i<i_len; i++) {
	    	var plant = plants[i];	
	    	
	    	// Loop per plant
	    	for (var j=0, j_len=p_number_tags.length; j<j_len; j++) {
	    		var p_no = p_number_tags[j];
				if ($.inArray(p_no, note_tags) === -1) continue; 

	    		// Create object if does not exist
				if (!notes_sorted.hasOwnProperty(plant)) 		notes_sorted[plant] = {};
				if (!notes_sorted[plant].hasOwnProperty(p_no)) 	notes_sorted[plant][p_no] = {};

				if (!notes_sorted[plant][p_no].hasOwnProperty(year)) {
				    notes_sorted[plant][p_no][year] = new Array(53);
				    for (var k = 0; k < 54; k++) {
				    	notes_sorted[plant][p_no][year][k] = {'notes': [], 'state':[], 'location': ''};
				    }
				}
			    
			    notes_sorted[plant][p_no][year][week].notes.push(note);

			    for (var k=0, k_len=states.length; k<k_len; k++) {
			    	if ($.inArray(states[k], notes_sorted[plant][p_no][year][week].state) !== -1) continue;
			    	notes_sorted[plant][p_no][year][week].state.push(states[k]);
			    }

			    // for (var k=0, k_len=locations.length; k<k_len; k++) {
			    // 	if ($.inArray(locations[k], notes_sorted[plant][p_no][year][week].location) !== -1) continue;
			    // 	notes_sorted[plant][p_no][year][week].location.push(locations[k]);
			    // }
			    if (locations.length > 0) {
				    for (var wk=week; wk<54; wk++){
				    	notes_sorted[plant][p_no][year][wk].location = locations;
				    }
			    }
	    		
	    	}
		}	
    }

    for (var plant in notes_sorted) {

    }

	console.timeEnd("sort_data");

	console.log(notes_sorted['7808a9a7-8ecc-472f-a06f-63290091d1ae']);
	console.log(notes_sorted['d7741d56-d4f3-4b0f-8a49-37c893f19db6']);
	console.log(notes_sorted);

	return notes_sorted;

}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenChart(notes_to_display, garden_data, state) {


	// Colors based on google's material design palette
	// https://material.google.com/style/color.html#color-color-palette
	var colors = {
		"light_purple": "#E1BEE7", 
		"purple": "#9C27B0", 
		"red": "#EF5350", 
		"lgreen": "#C5E1A5",
		"green": "#7CB342",
		"yellow": "#FFF176",
		"brown": "#BCAAA4",
		"orange": "#FFB74D",
		"blue": "#3949AB",
		"grey": "#E0E0E0",
		"teal": "#009688",
		"lime": "#CDDC39",
		"ldeep_orange": "#FFAB91",
		"deep_orange": "#FF5722",
		"blue_grey": "#607D8B",
		"cyan": "#00BCD4",
		"pink": "#E91E63",
		"lpink": "#F48FB1",
		"indigo": "#3F51B5",
		"amber": "#FFC107"

	}

	var location_colors = {
		"1c5facd7-7bbd-4b97-8af2-a46a522e2ba7": "cyan", 
		"5fad5a58-d839-4da7-a23b-eec95fae4ad4": "lime", 
		"326b7a7c-4298-4e08-9330-199a4b9ddff3": "indigo",
		"21305133-7020-4c0c-8a4e-a4b11b37eb4f": "deep_orange",
		"52c6eaac-26b4-4479-827f-6df0bd728226": "pink",
		"f03fa0eb-a5ec-4ab0-b87d-6eedffd10d92": "purple",
		"89e011c2-8a63-4a5c-be18-f8fe6b5e5e19": "blue_grey",
		"0fd778c4-b5ee-4c5a-849f-776dbd99dc21": "teal",
		"ff340368-9f93-432e-8495-9dc9f2269212": "amber"
	}



	console.time("draw_chart");


	var HTMLtable = '<div class="table-responsive"><table id="diary" class="table table-condensed"><thead><tr><th>Plant Name</th><th>Location</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table></div>';
	var HTML_cell = '<td %cell_colour% %border% nowrap><div style="cursor:pointer" data-toggle="popover" data-trigger="focus" data-placement="bottom" data-html="true" title="<b>%popover_title%</b>" data-content="<dl>%popover_body%</dl>">%plant_symbol%</div>';
	var HTML_loc_popover = '<a href="#" style="cursor:pointer" data-toggle="popover" data-trigger="focus" data-placement="bottom" data-html="true" title="<b>Location Color Key</b>" data-content="<dl>%popover_body%</dl>">KEY</a>';
	var HTML_popover_img = "<img src='%res_link%' width='200' />";
	var HTML_popover_link = "<dd><a href='%url%'>• %link_text%</a></dd>";


	var locations = garden_data.location_tags;

	var today = new Date();
	today_wk = today.getWeek(); // align to week 0
	today_yr = today.getFullYear().toString();

	//Sort location color key popover
	color_loc = [];
	for (var guid in location_colors) {
		color_loc.push("<font color='%color%'><b>".replace('%color%', colors[location_colors[guid]]));
		color_loc.push(locations[guid]);
		color_loc.push('</b></font><br>');
	}
	color_loc = color_loc.join('');
	HTML_loc_popover = HTML_loc_popover.replace('%popover_body%', color_loc);

	// Filter tags
	dead_tag = findKeyfromValue('*dead', garden_data.state_tags);
	moved_tag = findKeyfromValue('*moved', garden_data.state_tags);
	end_tag = findKeyfromValue('*end', garden_data.state_tags);

	if (!$('#watering_check').is(':checked'))  delete state[findKeyfromValue('*watering', garden_data.state_tags)];

	// Create week number table header
	var week_numbers = [];
	for (i = 0; i < 54; i++) {
		week_numbers.push('00'.substring(i.toString().length) + i.toString());
	}
	var HTML_header_week_no  = '<th>';
	HTML_header_week_no 	+= week_numbers.join('</th><th>');
	HTML_header_week_no 	+= '</th>';


	var HTML_row = [];
	for (var plant in notes_to_display) {
    	if (!notes_to_display.hasOwnProperty(plant)) continue;

		var location    = '',
			cell_colour = '',
			this_cell_colour = '';

		for (var year in notes_to_display[plant]) {
	    	if (!notes_to_display[plant].hasOwnProperty(year)) continue;

			HTML_row.push('<tr><td nowrap>');
			HTML_row.push(garden_data.plant_tags[plant]);
			HTML_row.push('</td><td nowrap>');
			//HTML_row.push(HTML_loc_popover);
			HTML_row.push('%location%');
			// HTML_row.push('</div>');
			HTML_row.push('</td>');

			// Reset variables
			var plant_dead  = false;

			HTML_row.push('<td>');
			HTML_row.push(year);
			HTML_row.push('</td>');

			// Loop through each week
			for (var week=0, week_len=notes_to_display[plant][year].length; week<week_len; week++) {

				var note = notes_to_display[plant][year][week];

				var formatted_HTML_cell = '<td %cell_colour% %border%></td>';

				this_cell_colour = cell_colour;

				// Clear cell contents for future weeks
				if((week > today_wk && year === today_yr) || plant_dead ){
					formatted_HTML_cell = '<td></td>';

				} else if (note.length > 0) {

					var popover_img 	= '',
						cell_symbols 	= '',
						popover_title 	= '',
						popover_body 	= '';

					if (this_cell_colour === '') {
						this_cell_colour = 'bgcolor="' + colors['lgreen'] + '"';
						cell_colour = this_cell_colour;
					}

					// Loop through all notes in the week
					for (var i=0, note_len=note.length; i<note_len; i++) {

						var tags = garden_data.notes[note[i]].tags;

						// Remove location tag if already registered
						if($.inArray(location, tags) !== -1) tags[tags.indexOf(location)] = '';

						// Loop through tags in note
						for (var j=0, j_len=tags.length; j<j_len; j++) {

							var tag = garden_data.notes[note[i]].tags[j];

							if ( state.hasOwnProperty(tag) ) {

								// Set cell color depending on plant state
								if( state[tag].color !== '' ) {
									this_cell_colour = 'bgcolor="';
									this_cell_colour += colors[state[tag].color] + '"';
									this_cell_colour += '"';
								
									if( state[tag].event === 'continous' ) cell_colour = this_cell_colour;
								}

								// Populate symbols for cell
								if (cell_symbols.indexOf(state[tag].symbol) === -1) {
									cell_symbols = cell_symbols + state[tag].symbol;
								}

								// Add image if present in note
								if(garden_data.notes[note[i]].res.length > 0) {
									popover_img = HTML_popover_img.replace('%res_link%', garden_data.notes[note[i]].res[0]);								
								}

								// Stop shading cells if plant has died
								if ( tag === dead_tag ) plant_dead = true;
								
								// Create popover or append if multiple notes in a single week
								title = garden_data.notes[note[i]].title.replace(/"/g, "'");
								popover_title = popover_title !== '' ? 'Multiple notes this week' : title;
								popover_body  = popover_body + HTML_popover_link.replace('%url%', garden_data.notes[note[i]].link);
								popover_body  = popover_body.replace('%link_text%', title);

							} else if ( locations.hasOwnProperty(tag) && (location === '' || $.inArray(moved_tag, tags) !== -1)) {
								location = tag;
							}
						}

					}
	
					// Draw cell
					formatted_HTML_cell = HTML_cell.replace('%popover_title%', popover_title);
					formatted_HTML_cell = formatted_HTML_cell.replace('%popover_body%', popover_body + popover_img);
					formatted_HTML_cell = formatted_HTML_cell.replace('%plant_symbol%', cell_symbols);
				}

				formatted_HTML_cell = formatted_HTML_cell.replace('%cell_colour%',  this_cell_colour);
				if (location){
					formatted_HTML_cell = formatted_HTML_cell.replace('%border%',  'style="border-bottom: 5px solid '+ colors[location_colors[location]]+';"');
				}
				HTML_row.push(formatted_HTML_cell);
			}	
			
			HTML_row[HTML_row.indexOf('%location%')] = locations[location]; 
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
	// $('#diary_length').append(HTML_loc_popover);

	// Enable popover
	$(document).ready(function() {
	    $("#chart-section").popover({ 
	    	selector: '[data-toggle=popover]',
	    	container : 'body'
	     });
	});

	$(document).ready(function() {
	    $('#diary').DataTable( {
        "scrollY": 400,
        "scrollX": 400,
        "fixedHeader": {
	        header: true
	    },
	    "search": {
			"regex": true
		},
        "scrollCollapse": true,
        "paging":         true,
        // "fixedColumns":   {
        //     "leftColumns": 2
        // },
        "columnDefs": [
	        { "targets": [0, 1, 2], "orderable": true},
	        { "targets": '_all', 	"orderable": false }
	    ]
    } );
	} );


	console.timeEnd("draw_chart");

}