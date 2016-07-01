//
// charts_update.js
// Will De Freitas
//
// Draws irrigation charts
//
// 


//-------------------------------------------------------------------------------
// Grab irrigation data from 
//-------------------------------------------------------------------------------
function displayIrrigation() {
	// Highlights correct navbar location
	$('li').removeClass('active');
	$('#irrig').parent().addClass('active');

	// Clear chart area
	$('#graph-container').empty();

	$.getJSON('weather_data/irrigation.json', function(json) {
	    drawIrrigation(json);
	});
    
}


//-------------------------------------------------------------------------------
// Draw charts
//-------------------------------------------------------------------------------
function drawIrrigation(chart_data) {

	// Create chart
	var title = '<div class="row"><h1>%name%</h1></div><div id="irrig_title"></div>';
    $(title.replace("%name%", 'irrigation')).appendTo('#graph-container');
    console.log(chart_data);


}



//-------------------------------------------------------------------------------
// If user has irrigated, save it to json file
//-------------------------------------------------------------------------------
function saveIrrigation() {

    var json = JSON.stringify(form_data);
    var encoded = btoa(json);

	$.ajax({
		url: 'php/save_irrig_data.php',
		type: "post",
		data: 'json=' + encoded,
		success: function(rxData) {
			alert(rxData);
	  }
	});

}


