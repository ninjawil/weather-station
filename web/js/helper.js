//-------------------------------------------------------------------------------
//
// The MIT License (MIT)
//
// Copyright (c) 2015 William De Freitas
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
//-------------------------------------------------------------------------------


//===============================================================================
// HTML Values
//===============================================================================
var HTMLerrorMSG	= '<div class="alert alert-danger alert-mod" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><strong><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>  %error_type%</strong>%error_msg%</div>';

var HTMLupdateTime = '<div class="row">%time%</div>';
var HTMLupdateDate = '<div class="row">%date%</div>';

var HTMLvalueBox = '<div id="%id%" class="row reading-group"><div class="row reading-name">%description%</div></div>';
var HTMLvalue = '<div class="row reading-value">%value%<span class="reading-unit"> %unit%</span></div>';

var HTMLlogBox = '<h4>%logFileName%</h4><pre id="%logName%" class="log-display"></pre>';

