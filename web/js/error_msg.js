//
// charts_update.js
// Will De Freitas
//
// Displays error messages based on xml files
//
// 


//-------------------------------------------------------------------------------
// Pads a number with zeros
//-------------------------------------------------------------------------------
function pad(num, size) {
    var s = "000" + num;
    return s.substr(s.length-size);
}


//-------------------------------------------------------------------------------
// Grab error.json data
//-------------------------------------------------------------------------------
function grabConfigData(){

	$.getJSON('weather_data/error.json', function(json) {
	    displayErrorMessage(json);
	});

}


//-------------------------------------------------------------------------------
// Manages error messages depending on passed error code
//-------------------------------------------------------------------------------
function displayErrorMessage(json) {

	error_data = json;

	errorValue = 0;
	errorMessage = '';

	for (var error in error_data) {
		if(error_data[error].time != 0) {
			errorValue = error;
			errorMessage = error_data[error].msg;
		}
	};

	if(errorValue != 0){

		var displayErrorType = "   Error E"+ pad(errorValue, 4) + ": ";

		var formattedErrorMsg = HTMLerrorMSG.replace("%error_type%", displayErrorType);
		formattedErrorMsg = formattedErrorMsg.replace("%error_msg%", errorMessage);

		$('#error_display').append(formattedErrorMsg);
	}
}


//-------------------------------------------------------------------------------
// Prepares data and displays it
//-------------------------------------------------------------------------------
function main() {

	grabConfigData();
}


//===============================================================================
// Main
//===============================================================================
main();


