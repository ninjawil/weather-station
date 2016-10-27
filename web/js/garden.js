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

	console.time("search_bar");

	// var HTMLPlantFilter = '<div id="bar1" class="col-md-4">%bar1%</div><div id="bar2" class="col-md-4">%bar2%</div><div id="bar3" class="col-md-2">%bar3%</div><div id="bar4" class="col-md-1">%bar4%</div><div id="bar5" class="col-md-1" style="top: 25px;;">%bar5%</div>',
	var HTMLPlantFilter = '<div id="bar1" class="col-md-4">%bar1%</div><div id="bar3" class="col-md-2">%bar3%</div><div id="bar4" class="col-md-1">%bar4%</div><div id="bar5" class="col-md-1" style="top: 25px;">%bar5%</div>',
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
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar2%', HTMLlocList.replace("%loc_list%", locations.join('</option><option>')));
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar3%', HTMLdateList.replace("%date_list%", year_list.join('</option><option>')));
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar4%', HTMLoptionsList)
	f_HTMLPlantFilter 		= f_HTMLPlantFilter.replace('%bar5%', HTMLfilterButton)

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

        var sorted_data = sortGardenData(garden_data, search_data);

        getFileData('weather_data/state_tags.json', 'json', drawGardenChart, [sorted_data, garden_data]);

    }); 

}



//-------------------------------------------------------------------------------
// Sorts garden data
//-------------------------------------------------------------------------------
function sortGardenData(garden_data, search) {

	console.time("sort_data");

	var dead_plants = [],
		dead = false;

	var dead_tag = findKeyfromValue('*dead', garden_data.state_tags);


    // Filter notes
    var notes_sorted = {};
    for (var note in garden_data.notes) {
		if (!garden_data.notes.hasOwnProperty(note)) continue;
 
    	var date = new Date(Number(garden_data.notes[note].created));
    	var year = date.getFullYear().toString();
		var week = date.getWeek();

		var note_tags = garden_data.notes[note].tags;

    	dead = ($.inArray(dead_tag, note_tags) !== -1) ? true : false;

    	if ($.inArray(year, search.year) === -1) continue

    	//if ($.inArray(year, search.location) === -1) continue   	

	    for (var i=0, i_len=search.plant.length; i<i_len; i++) {
		    if ($.inArray(search.plant[i], note_tags) === -1) continue	 

    		// Create object if does not exist
			if (!notes_sorted.hasOwnProperty(search.plant[i])) {
				notes_sorted[search.plant[i]] = {};
			}

			if (!notes_sorted[search.plant[i]].hasOwnProperty(year)) {
			    notes_sorted[search.plant[i]][year] = [ 
			    	[], [], [], [], [], [], [], [], [], [],
			    	[], [], [], [], [], [], [], [], [], [],
			    	[], [], [], [], [], [], [], [], [], [],
			    	[], [], [], [], [], [], [], [], [], [],
			    	[], [], [], [], [], [], [], [], [], [],
			    	[], [], [], []
			    ];
			}

	    	if (dead) dead_plants.push(search.plant[i]);

	    	// console.log(notes_sorted[search.plant[i]]);
	    	// console.log(garden_data.notes[note].title);
	    	// console.log(garden_data.plant_tags[search.plant[i]]);
	    	// console.log(year);
	    	// console.log(week);

	    	notes_sorted[search.plant[i]][year][week].push(note);
		    
		}	
    }

    // Remove dead plants
    if (search.alive === "checked") {
	    for (var i = dead_plants.length - 1; i >= 0; i--) {
	    	delete notes_sorted[dead_plants[i]];
	    }
	}

	console.timeEnd("sort_data");

	return notes_sorted;

}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenChart(notes_to_display, garden_data, state) {


	console.time("draw_chart");


	var HTMLtable = '<div class="table-responsive"><table id="diary" class="table table-condensed"><thead><tr><th>Plant Name</th><th>Location</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table></div>';
	var HTML_cell = '<td %cell_colour% nowrap><div style="cursor:pointer" data-toggle="popover" data-trigger="focus" data-placement="bottom" data-html="true" title="<b>%popover_title%</b>" data-content="<dl>%popover_body%</dl>">%plant_symbol%</div>';
	var HTML_popover_img = "<img src='%res_link%' width='200' />";
	var HTML_popover_link = "<dd><a href='%url%'>• %link_text%</a></dd>";

	var locations = garden_data.location_tags;

	var today = new Date();
	today_wk = today.getWeek(); // align to week 0
	today_yr = today.getFullYear().toString();


	// Filter tags
	dead_tag = findKeyfromValue('*dead', garden_data.state_tags);

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

		var cell_colour = '',
			this_cell_colour = '';

		for (var year in notes_to_display[plant]) {
	    	if (!notes_to_display[plant].hasOwnProperty(year)) continue;

			HTML_row.push('<tr><td nowrap>');
			HTML_row.push(garden_data.plant_tags[plant]);
			HTML_row.push('</td><td nowrap>');
			HTML_row.push('%location%');
			HTML_row.push('</td>');

			// Reset variables
			var location    = '',
				popover_img = '',
				plant_dead  = false;

			HTML_row.push('<td>');
			HTML_row.push(year);
			HTML_row.push('</td>');

			// Loop through each week
			for (var week=0, week_len=notes_to_display[plant][year].length; week<week_len; week++) {

				var note = notes_to_display[plant][year][week];

				var formatted_HTML_cell = '<td %cell_colour%></td>';

				this_cell_colour = cell_colour;

				// Clear cell contents for future weeks
				if((week > today_wk && year === today_yr) || plant_dead ){
					formatted_HTML_cell = '<td></td>';

				} else if (note.length > 0) {

					var cell_symbols 	= '',
						popover_title 	= '',
						popover_body 	= '';

					if (this_cell_colour === '') {
						this_cell_colour = 'class="success"';
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
									this_cell_colour = 'class="';
									this_cell_colour += state[tag].color + '"';
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
								
							} else if ( locations.hasOwnProperty(tag) ){
								location = tag;
							}
						}

						// Create popover or append if multiple notes in a single week
						title = garden_data.notes[note[i]].title.replace(/"/g, "'");
						popover_title = popover_title !== '' ? 'Multiple notes this week' : title;
						popover_body  = popover_body + HTML_popover_link.replace('%url%', garden_data.notes[note[i]].link);
						popover_body  = popover_body.replace('%link_text%', title);

					}
	
					// Create popover			
					formatted_HTML_cell = HTML_cell.replace('%popover_title%', popover_title);
					formatted_HTML_cell = formatted_HTML_cell.replace('%popover_body%', popover_body + popover_img);
					
					// Draw cell
					formatted_HTML_cell = formatted_HTML_cell.replace('%plant_symbol%', cell_symbols);

				}

				formatted_HTML_cell = formatted_HTML_cell.replace('%cell_colour%',  this_cell_colour);
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