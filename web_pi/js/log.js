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
		log_no = 0;

	var directory = 'weather_logs/',
		filenames = [	'irrigation.log', 
						'read_sensors.log', 
						'read_rain_gauge.log', 
						'rrd_export.log', 
						'rrd_ts_sync.log', 
						'rrd_switch.log', 
						'watchdog.log', 
						'weekly_summary.log'];

	$('#panel_group').empty();

	for(var filename in filenames) {

		console.log(filename);

		// Prepare log menu
		formattedHTMLlogCollapse = HTMLlogCollapse.replace('%collapse_no%', 'logCollapse' + log_no);
		formattedHTMLlogCollapse = formattedHTMLlogCollapse.replace('%collapse_no%', 'logCollapse' + log_no);
		formattedHTMLlogCollapse = formattedHTMLlogCollapse.replace('%collapse_name%', filenames[filename]);

		//Prepare log box
		formattedHTMLlogCollapse = formattedHTMLlogCollapse.replace('%logFileName%', filenames[filename]);
		formattedHTMLlogCollapse = formattedHTMLlogCollapse.replace('%logName%', filenames[filename].slice(0, -4));
		$('#panel_group').append(formattedHTMLlogCollapse);

		//Write log data
		logGetData(directory, filenames[filename]);

		log_no = log_no + 1;
	}
	// }
		
	$('#modal_logs').modal('show');

}

