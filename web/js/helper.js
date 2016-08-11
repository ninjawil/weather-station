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

var HTMLerrorTable = '<tr><td>%date%</td><td>%errornumber%</td><td>%message%</td><td>%notified%</td><td>%count%</td></tr>';

var HTMLallDropdown = '<li><a href="#" onclick="displayHeatMap(%id%)">%name%</a></li>';

var HTMLirrigButton = '<div class="btn-group"><button class="btn btn-default btn-lg dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Water appled <span class="caret"></span></button><ul class="dropdown-menu"><li><a href="#">Fully watered</a></li><li><a href="#">Partially watered</a></li></ul></div>';

var HTMLlogBox = '<h4>%logFileName%</h4><pre id="%logName%" class="log-display"></pre>';
var HTMLlogFileSelect = '<option>%logFileName%</option>';
var HTMLcolumns = '<div class="row"><div id="log_modal_col_1" class="col-md-6"></div><div id="log_modal_col_2" class="col-md-6"></div></div>';

var HTMLlogCollapse = '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a data-toggle="collapse" href="#%collapse_no%">%collapse_name%</a></h4></div><div id="%collapse_no%" class="panel-collapse collapse"><div class="panel-body"><pre id="%logName%" class="log-display"></pre></div></div></div>';
