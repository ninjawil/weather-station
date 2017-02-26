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
var HTMLerrorMSG = '<div class="alert alert-danger alert-mod" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><span id="err_table_link" class="glyphicon glyphicon-new-window" aria-hidden="true" data-toggle="modal" data-target="#modal_errors"></span><strong>%error_type%</strong>%error_msg%</div>';

var HTMLerrorTable = '<tr><td>%date%</td><td>%errornumber%</td><td>%message%</td><td>%notified%</td><td>%count%</td></tr>';

var HTMLirrig = '<div class="panel panel-default" style="margin-top: 20px;"><div class="panel-heading">Irrigation Amount</div><div class="panel-body"><div class="row"><div class="col-md-2">%col1%</div><div class="col-md-10"><div class="irrig-bar">%col2%</div></div></div></div>';
var HTMLirrigButton = '<div class="btn-group" role="group" aria-label="..."><button id="irrig-minus-btn" type="button" class="btn btn-default"><span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button> <button id="irrig-plus-btn" type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span></button><button id="irrig-save-btn" type="button" class="btn btn-default"><span class="%disk_icon%" aria-hidden="true"></span></button></div>';
var HTMLirrigBar = '<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="%barvalue%" aria-valuemin="0" aria-valuemax="100" style="width: %barvalue%%;">%irrig_amount% / %irrig_depth_full%mm  %barvalue%%</div></div></div>';


var HTMLlogBox = '<h4>%logFileName%</h4><pre id="%logName%" class="log-display"></pre>';
var HTMLlogFileSelect = '<option>%logFileName%</option>';
var HTMLcolumns = '<div class="row"><div id="log_modal_col_1" class="col-md-6"></div><div id="log_modal_col_2" class="col-md-6"></div></div>';

var HTMLlogCollapse = '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a data-toggle="collapse" href="#%collapse_no%">%collapse_name%</a></h4></div><div id="%collapse_no%" class="panel-collapse collapse"><div class="panel-body"><pre id="%logName%" class="log-display"></pre></div></div></div>';
