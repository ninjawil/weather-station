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
function grabErrorData(functionCall, args){

	$.getJSON('weather_data/error.json', function(json) {
		//functionCall(json, true);
		args.push(json);
		functionCall.apply(this, args);
	});

}


//-------------------------------------------------------------------------------
// Grab error.json data
//-------------------------------------------------------------------------------
function clearErrors(){

	$.get('php/clear_errors.php', function(data) {
	  	alert(data);
	});

}


//-------------------------------------------------------------------------------
// Manages error messages depending on passed error code
//-------------------------------------------------------------------------------
function displayErrorMessage(error_data, display_err_code= true, display_err_table_link= true) {


	$('#error_display').empty();

	errorValue = 0;
	errorMessage = '';

	for (var error in error_data) {
		if(error_data[error].time != 0) {
			errorValue = error;
			errorMessage = error_data[error].msg;
		}
	};

	if(errorValue != 0){

		var displayErrorType = "   Error";
		
		if(display_err_code != false){
			displayErrorType = displayErrorType + " E"+ pad(errorValue, 4);
		}
		
		var formattedErrorMsg 	= HTMLerrorMSG.replace("%error_type%", displayErrorType + ": ");
		formattedErrorMsg 		= formattedErrorMsg.replace("%error_msg%", errorMessage);

		$('#error_display').append(formattedErrorMsg);
		
		if(display_err_table_link != true){
			$('span').remove("#err_table_link");
		}
	}
}


//-------------------------------------------------------------------------------
// Parses error messages to error table
//-------------------------------------------------------------------------------
function parseErrorMsgTable(error_data) {

	// Sort by error date
	keysSorted = Object.keys(error_data).sort(function(a,b){return a.time-b.time});


	for (var i=0,  tot=keysSorted.length; i < tot; i++) {
		if(error_data[keysSorted[i]].time != 0) {

			var datetime = new Date(error_data[keysSorted[i]].time * 1000);
			datetime = datetime.toUTCString();

			var formattedError 	= HTMLerrorTable.replace("%date%", datetime);
			formattedError 		= formattedError.replace("%errornumber%", keysSorted[i]);
			formattedError 		= formattedError.replace("%message%", error_data[keysSorted[i]].msg);
			formattedError 		= formattedError.replace("%count%", error_data[keysSorted[i]].count);

			var notified = 'No';
			
			if(error_data[keysSorted[i]].notified === '1') { notified = 'YES' }
			formattedError 		= formattedError.replace("%notified%", notified);

			$('#error_table').append(formattedError);
		}
	}
}


//-------------------------------------------------------------------------------
// Prepares data and displays it
//-------------------------------------------------------------------------------
function main() {

	grabErrorData(displayErrorMessage, []);

	$('#modal_errors').on('shown.bs.modal', function (e) {
    	grabErrorData(parseErrorMsgTable, []);
	});

	$('#modal_errors').on('hidden.bs.modal', function (e) {
    	$('#error_table').empty()
	});
}


//===============================================================================
// Main
//===============================================================================
main();


