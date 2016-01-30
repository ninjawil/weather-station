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
// Manages error messages depending on passed error code
//-------------------------------------------------------------------------------
function displayErrorMessage(errorValue) {

	var errors = {};
	errors = {
		1: ["Error", "There is an error!"],
		2: ["Error", "There is an error!"],
		3: ["Warning", "There is a warning!"],
		4: ["Error", "There is an error!"]
	};

	var errorMessage = errors[errorValue][0] + " E"+ pad(errorValue, 3) + ": ";

	var formattedErrorMsg = HTMLerrorMSG.replace("%error_type%", errorMessage);
	formattedErrorMsg = formattedErrorMsg.replace("%error_msg%", errors[errorValue][1]);

	$('#error_display').append(formattedErrorMsg);
}



//-------------------------------------------------------------------------------
// Prepares data and displays it
//-------------------------------------------------------------------------------
function main() {

	var systemError = 0;

	if(systemError) {
		displayErrorMessage(systemError);
	};
}


//===============================================================================
// Main
//===============================================================================
main();


