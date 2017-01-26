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
	var today_wk = today.getWeek(); // align to week 0
	var today_yr = today.getFullYear().toString();

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

	var notes_to_display = notes_to_display.diary;

	for(plant in notes_to_display) {
		if (!notes_to_display.hasOwnProperty(plant)) continue;

		// if (plant != 'eaae0e6d-f694-458a-a4ea-d4f44f4e92d6') continue;

		var this_cell_colour = '',
			cell_colour = '',
			this_border_colour = '',
			this_location = '';

		for(plant_no in notes_to_display[plant]) {
			if (!notes_to_display[plant].hasOwnProperty(plant_no)) continue;

			// Collate all years to today
			var years = Object.keys(notes_to_display[plant][plant_no]['timeline']);
			years = years.map(Number);
			var year_first = Math.min.apply(null, years);

			// Loop through the years
			for (var year=year_first; year<=today_yr; year++) {

				// Exit loop if plant has died and no more notes in the timeline
				if ((years.indexOf(year) == -1) && plant_dead) break;

				// Populate row contents
				HTML_row.push('<tr><td nowrap>');
				HTML_row.push(plants[plant].replace(/#/g, ''));
				HTML_row.push('</td><td nowrap>');
				HTML_row.push(Number(plant_no).toFixed(2));
				HTML_row.push('</td><td nowrap>');
				HTML_row.push('%location%');
				HTML_row.push('</td><td>');
				HTML_row.push(year);
				HTML_row.push('</td>');

				// Loop through each week
				for (var week=1, week_len=53; week<=week_len; week++) {

					var week_entry = '';
					if (notes_to_display[plant][plant_no]['timeline'].hasOwnProperty(year)){
						week_entry = notes_to_display[plant][plant_no]['timeline'][year][week-1];
					} 
					
					// Clear week colors for future weeks or if plant has died
					if ((week >= today_wk+1 && year == today_yr) || plant_dead) {
						cell_colour = '';
						this_border_colour = '';
					}			

					this_cell_colour = cell_colour;

					if (week_entry) {

						// Set default cell colour
						if (this_cell_colour == '') this_cell_colour =  colors["lgreen"];

						var plant_dead  = false;
						if( week_entry.event == 'dead' ) plant_dead  = true;

						// Set cell color depending on plant state
						if( week_entry.color.length > 0 ) {
							var idx = 0;
							//if(week_entry.color.length > 1 && week_entry.color[idx] == "lgreen") idx++;
							if(week_entry.color.indexOf("lgreen") != -1) idx = week_entry.color.indexOf("lgreen");
							if(week_entry.color.indexOf("green") != -1) idx = week_entry.color.indexOf("green");
							if(week_entry.color.indexOf("light_purple") != -1) idx = week_entry.color.indexOf("light_purple");
							if(week_entry.color.indexOf("brown") != -1) idx = week_entry.color.indexOf("brown");
							if(week_entry.color.indexOf("red") != -1) idx = week_entry.color.indexOf("red");

							this_cell_colour = colors[week_entry.color[idx]];
						}

						if( week_entry.event == 'end' ) cell_colour = colors["lgreen"];
						if( (week_entry.event == 'continous')||(week_entry.event == 'start') ) {
							cell_colour = this_cell_colour;
						}

						var previous_location = '';
						if (week_entry.symbols.indexOf('m') != -1) {
							previous_location = locations[this_location] + " <span class='glyphicon glyphicon-arrow-right'></span> ";
						}

						// Set border colour for location
						if (week_entry.locations.length > 0  && (week_entry.symbols.indexOf('m') != -1 || this_border_colour == '')) {
							var idx = 0;
							if(week_entry.locations.length > 1 && week_entry.locations[idx] == this_location) idx++;
							this_location = week_entry.locations[idx];
							this_border_colour = 'style="border-bottom: 5px solid '+ colors[location_colors[this_location]]+';"';
						}

						var note_title = "<span class='ion-android-pin'></span> " + previous_location + locations[this_location];

						// Draw cell
						var popover_body  = ''; 
						for (var t=0, t_len=week_entry.body.length; t<t_len; t++){
							popover_body += HTML_popover_link.replace('%url%', week_entry.body[t][1]);
							popover_body  = popover_body.replace('%link_text%', week_entry.body[t][0]);
						}
						
						var popover_img = HTML_popover_img.replace('%res_link%', week_entry.image);

						formatted_HTML_cell = HTML_cell.replace('%cell_contents%', HTML_cell_content);
						formatted_HTML_cell = formatted_HTML_cell.replace('%popover_title%', note_title);
						formatted_HTML_cell = formatted_HTML_cell.replace('%popover_body%', popover_body + popover_img);
						formatted_HTML_cell = formatted_HTML_cell.replace('%plant_symbol%', week_entry.symbols.join(' '));
					} else {
						formatted_HTML_cell = HTML_cell.replace('%cell_contents%', '');
					}
	 
					formatted_HTML_cell = formatted_HTML_cell.replace('%border%',  this_border_colour);
					formatted_HTML_cell = formatted_HTML_cell.replace('%cell_colour%',  'bgcolor="'+this_cell_colour+'"');
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