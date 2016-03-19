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
function grabErrorData(functionCall){

	$.getJSON('weather_data/error.json', function(json) {
		functionCall(json);
	});

}


//-------------------------------------------------------------------------------
// Manages error messages depending on passed error code
//-------------------------------------------------------------------------------
function displayErrorMessage(error_data) {

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

		var formattedErrorMsg 	= HTMLerrorMSG.replace("%error_type%", displayErrorType);
		formattedErrorMsg 		= formattedErrorMsg.replace("%error_msg%", errorMessage);

		$('#error_display').append(formattedErrorMsg);
	}
}


//-------------------------------------------------------------------------------
// Parses error messages to error table
//-------------------------------------------------------------------------------
function parseErrorMsgTable(error_data) {

	for (var error in error_data) {
		if(error_data[error].time != 0) {

			var datetime = new Date(error_data[error].time);
			datetime = datetime.toUTCString();

			var formattedError 	= HTMLerrorTable.replace("%date%", datetime);
			formattedError 		= formattedError.replace("%errornumber%", error);
			formattedError 		= formattedError.replace("%message%", error_data[error].msg);

			var notified = 'No';
			
			if(error_data[error].notified === '1') { notified = 'YES' }
			formattedError 		= formattedError.replace("%notified%", notified);

			$('#error_table').append(formattedError);
		}
	}
}


//-------------------------------------------------------------------------------
// Prepares data and displays it
//-------------------------------------------------------------------------------
function main() {

	grabErrorData(displayErrorMessage);

	$('#modal_errors').on('shown.bs.modal', function (e) {
    	grabErrorData(parseErrorMsgTable);
	});

	$('#modal_errors').on('hidden.bs.modal', function (e) {
    	$('#error_table').empty()
	});
}


//===============================================================================
// Main
//===============================================================================
main();


