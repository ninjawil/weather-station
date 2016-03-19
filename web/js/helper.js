//
// helper.js
// Will De Freitas
//
// helpers
//
// 


//===============================================================================
// HTML Values
//===============================================================================
var HTMLerrorMSG	= '<div class="alert alert-danger alert-mod" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><span class="glyphicon glyphicon-new-window" aria-hidden="true" data-toggle="modal" data-target="#modal_errors"></span><strong>%error_type%</strong>%error_msg%</div>';

var HTMLupdateTime = '<div class="row">%time%</div>';
var HTMLupdateDate = '<div class="row">%date%</div>';

var HTMLvalueBox = '<div id="%id%" class="row reading-group"><div class="row reading-name">%description%</div></div>';
var HTMLvalue = '<div class="row reading-value">%value%<span class="reading-unit"> %unit%</span></div>';

var HTMLlogBox = '<h4>%logFileName%</h4><pre id="%logName%" class="log-display"></pre>';

var HTMLerrorTable = '<tr><td>%date%</td><td>%errornumber%</td><td>%message%</td><td>%notified%</td><td>%count%</td></tr>';

