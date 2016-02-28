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

	if(error_data.error_1.active == 1)
	{
		errorValue = 1;
		errorType = error_data.error_1.type;
		errorMessage = error_data.error_1.message;
	}

	var displayErrorType = errorType + " E"+ pad(errorValue, 3) + ": ";

	var formattedErrorMsg = HTMLerrorMSG.replace("%error_type%", displayErrorType);
	formattedErrorMsg = formattedErrorMsg.replace("%error_msg%", errorMessage);

	$('#error_display').append(formattedErrorMsg);
}


//-------------------------------------------------------------------------------
// Displays next error
//-------------------------------------------------------------------------------
$(document).ready(function(){
    $(".close").click(function(){
        $("#myAlert").alert("close");
    });
    $("#myAlert").on('closed.bs.alert', function(){
        console.log('closed and run again!');
        grabConfigData();
    });
});

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


