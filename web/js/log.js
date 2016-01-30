//
// charts_update.js
// Will De Freitas
//
// Displays log messages
//
// 


//-------------------------------------------------------------------------------
// Gets data from log file
//-------------------------------------------------------------------------------
function logGetData(directory, filename) {

	$.ajax({
        async:false,
        url: directory + '_logs/' + filename,
        dataType: 'text',
        success: function(data) 
        	{
	        	$('#' + filename.slice(0, -4)).append(data);
            }
        });
}


//-------------------------------------------------------------------------------
// Organizes log boxes in modal
//-------------------------------------------------------------------------------
function displayLogData(directory, filenames) {

	var columnNumber = 1,
		formattedHTMLlogBox = '';

	for(var logFile in filenames) {

		//Prepare HTML with log file details
		formattedHTMLlogBox = HTMLlogBox.replace('%logFileName%', filenames[logFile]);
		formattedHTMLlogBox = formattedHTMLlogBox.replace('%logName%', filenames[logFile].slice(0, -4));
		$('#log_modal_col_' + columnNumber).append(formattedHTMLlogBox);

		//Write log data
		logGetData(directory, filenames[logFile]);

		//Alternate columns
		columnNumber = (columnNumber === 1) ? 2 : 1;
	}
}


//-------------------------------------------------------------------------------
// Prepares data and displays it
//-------------------------------------------------------------------------------
function main() {

	var dir = 'weather',
		logFiles = ['read_sensors.log', 'read_rain_gauge.log', 'rrd_export.log', 'rrd_ts_sync.log', 'rrd_switch.log'];

	displayLogData(dir, logFiles);

}


//===============================================================================
// Main
//===============================================================================
main();

