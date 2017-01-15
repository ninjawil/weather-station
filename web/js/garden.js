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
    // getFileData('weather_data/gardening_web.json', 'json', drawGardenSearchBar, []);
    getFileData('weather_data/gardening_web.json', 'json', drawGardenChart, []);
	//getFileData('weather_data/state_tags.json', 'json', drawGardenChart, [sorted_data, garden_data]);


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

        getFileData('weather_data/state_tags.json', 'json', drawGardenChart, [garden_data.diary, garden_data]);

    }); 

}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawGardenChart(notes_to_display) {


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


	console.time("sort_data");

	var HTMLtable 			= '<div class="table-responsive"><table id="diary" class="table table-condensed"><thead><tr><th>Plant Name</th><th>No.</th><th>Location</th><th>Year</th>%week_no%</tr></thead><tbody id="plant-table">%plants%</tbody></table></div>';
	var HTML_cell 			= '<td %cell_colour% %border% nowrap>%cell_contents%</td>'
	var HTML_cell_content 	= '<div style="cursor:pointer" data-toggle="popover" data-trigger="focus" data-placement="bottom" data-html="true" title="<b>%popover_title%</b>" data-content="<dl>%popover_body%</dl>">%plant_symbol%</div>';
	var HTML_loc_popover 	= '<a href="#" style="cursor:pointer" data-toggle="popover" data-trigger="focus" data-placement="bottom" data-html="true" title="<b>Location Color Key</b>" data-content="<dl>%popover_body%</dl>">KEY</a>';
	var HTML_popover_img 	= "<img src='%res_link%' width='200' />";
	var HTML_popover_link 	= "<dd><a href='%url%'>• %link_text%</a></dd>";


	var locations = notes_to_display.location_tags;
	var plants = notes_to_display.plant_tags;

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


	// Create week number table header
	var week_numbers = [];
	for (i = 1; i < 54; i++) {
		week_numbers.push('00'.substring(i.toString().length) + i.toString());
	}
	var HTML_header_week_no  = '<th>';
	HTML_header_week_no 	+= week_numbers.join('</th><th>');
	HTML_header_week_no 	+= '</th>';

	var HTML_row = [];

	// var plant = '644f1488-5a31-458a-b2e1-921a92243048'; 	// Acer palmatum
	// var plant = '88925827-d549-4142-9408-02bc8ed4fb7b'; 	// Acer 'unknown'
	//var plant = '38a557af-4e6f-4d65-b0a1-b84674246434'; 	// abies koreana
	// var plant = '79dd2419-c744-4889-9ba1-3c1fb4e3bcd3'; 	//achillea 'terracota'
	//var plant = '553aaad1-5852-45fc-b3ce-492ba27cf817'; 		// #agapanthus 'dr brouwer'
	// var plant = '0dc6cb1f-f616-4bfb-a1c6-89bd1a90fda7'; 		// #Ageratina altissima	Chocolate
	// var plant = 'dfbaaa4f-ad84-4abd-8bbf-d09c5d69e0b5'; 		// #Allium oreophilum
	// var plant = 'b89ed552-3837-4b0c-872b-d73a9e361533'; 		// #allium cristophii "star of persia"
	// var plant = "e789f7e5-4a4c-4a38-934b-aa1d996509d0"; 		// #allium 'gladiator'

	notes_to_display = notes_to_display.diary;

	for(plant in notes_to_display) {
		if (!notes_to_display.hasOwnProperty(plant)) continue;

		var this_cell_colour = '',
			cell_colour = '',
			this_location = '';

		for(plant_no in notes_to_display[plant]) {
			if (!notes_to_display[plant].hasOwnProperty(plant_no)) continue;

			// Collate all years and if current year not there then add it
			years = Object.keys(notes_to_display[plant][plant_no]['timeline']);
						
			if (years.indexOf(today_yr) == -1 && 
				notes_to_display[plant][plant_no]['status'] != 'dead') {
				years.push(today_yr);
			}

			
			for (i=0, i_len=years.length; i<i_len; i++) {

				year = years[i];

				HTML_row.push('<tr><td nowrap>');
				HTML_row.push(plants[plant]);
				HTML_row.push('</td><td nowrap>');
				HTML_row.push(plant_no);
				HTML_row.push('</td><td nowrap>');
				HTML_row.push('%location%');
				HTML_row.push('</td><td>');
				HTML_row.push(year);
				HTML_row.push('</td>');

				// Exit loop is year is not in records

				// Loop through each week
				for (var week=1, week_len=53; week<=week_len; week++) {

					var week_entry = '';
					
					if (notes_to_display[plant][plant_no]['timeline'].hasOwnProperty(year)){
						week_entry = notes_to_display[plant][plant_no]['timeline'][year][week-1];
					} 
					
					if (week >= today_wk+1 && year == today_yr) {
						// Clear week colors for future weeks
						cell_colour = '';
					}			

					this_cell_colour = cell_colour;

					if (week_entry) {

						// Reset variables
						var plant_dead  = false;

						// Set cell color depending on plant state
						if( week_entry.color.length > 0 ) {
							var idx = 0;
							if(week_entry.color.length > 1 && week_entry.color[idx] == "lgreen") {
								idx++;
							}

							this_cell_colour = 'bgcolor="';
							this_cell_colour += colors[week_entry.color[idx]] + '"';
							this_cell_colour += '"';
						
							if( week_entry.event == 'continous' ) cell_colour = this_cell_colour;
							if( week_entry.event == 'dead' ) {
								plant_dead  = true;								
								cell_colour = '';
							}
						}

						// Set location
						this_location = week_entry.locations[0];

						// Draw cell
						var popover_body  = '';
						for (var t=0, t_len=week_entry.body.length; t<t_len; t++){
							popover_body += HTML_popover_link.replace('%url%', week_entry.body[t][1]);
							popover_body  = popover_body.replace('%link_text%', week_entry.body[t][0]);
						}
						
						var popover_img = HTML_popover_img.replace('%res_link%', week_entry.image);

						formatted_HTML_cell = HTML_cell.replace('%cell_contents%', HTML_cell_content);
						formatted_HTML_cell = formatted_HTML_cell.replace('%popover_title%', week_entry.title);
						formatted_HTML_cell = formatted_HTML_cell.replace('%popover_body%', popover_body + popover_img);
						formatted_HTML_cell = formatted_HTML_cell.replace('%plant_symbol%', week_entry.symbols.join(' '));

					} else {
						formatted_HTML_cell = HTML_cell.replace('%cell_contents%', '');
						formatted_HTML_cell = formatted_HTML_cell.replace('%border%', '');
					}
	 
					formatted_HTML_cell = formatted_HTML_cell.replace('%cell_colour%',  this_cell_colour);
					HTML_row.push(formatted_HTML_cell);
				}

				// Update with final year's location
				HTML_row[HTML_row.indexOf('%location%')] = locations[this_location];

			}
		}
	}

	// Draw row
	HTML_row.push('</tr>');

	console.timeEnd("sort_data");
	console.time("draw_chart");

	// Clear chart area
	$('#chart-section').empty();

	// Draw table
    formattedHTMLtable = HTMLtable.replace('%week_no%', HTML_header_week_no);
    formattedHTMLtable = formattedHTMLtable.replace('%plants%', HTML_row.join(''));
    formattedHTMLtable = formattedHTMLtable.replace(/@/g, '');
    formattedHTMLtable = formattedHTMLtable.replace(/\+p/g, '');
    formattedHTMLtable = formattedHTMLtable.replace(/#/g, '');
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