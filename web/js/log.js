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

	var rawFile = new XMLHttpRequest();
    rawFile.open("GET", directory + filename, true);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                $('#' + filename.slice(0, -4)).append(rawFile.responseText);
            }
        }
    }
    rawFile.send(null);

}


//-------------------------------------------------------------------------------
// Organizes log boxes in modal
//-------------------------------------------------------------------------------
function displayLogData() {

	var columnNumber = 1,
		log = 0,
		formattedHTMLlogBox = '';

	var directory = 'weather_logs/',
		filenames = ['read_sensors.log', 'read_rain_gauge.log', 'rrd_export.log', 'rrd_ts_sync.log', 'rrd_switch.log', 'watchdog.log'];

	for(var logFile in filenames) {
		formattedHTMLlogFileSelect = HTMLlogFileSelect.replace('%logFileName%', filenames[logFile]);
		$('#logFileSelect').append(formattedHTMLlogFileSelect);
	}

	$('#modal_logs').modal('show');

	$(#'show_log').click(function(){
		if(filenames.length > 2) {
			$('#log_file_modal_body').append(HTMLcolumns);
		}

		for(var logFile in filenames) {

			//Prepare HTML with log file details
			formattedHTMLlogBox = HTMLlogBox.replace('%logFileName%', filenames[logFile]);
			formattedHTMLlogBox = formattedHTMLlogBox.replace('%logName%', filenames[logFile].slice(0, -4));
			$('#log_modal_col_' + columnNumber).append(formattedHTMLlogBox);

			//Write log data
			logGetData(directory, filenames[logFile]);

			log = log + 1;
			if(log > 1) {
				columnNumber = 2;
			}
		}
	}
		
}

