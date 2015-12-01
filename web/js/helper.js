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
var HTMLerrorMSG	= '<div class="media" data-toggle="modal" data-target="#modal_errors"><a href="#" class="pull-left"><img src="images/warning.png" class="img-responsive" alt="error image"></a><div class="media-body error-text"><h4 class="media-heading">%error_type%</h4><p>%error_msg%</p></div></div>';

var HTMLupdateTime = '<div class="row">%time%</div>';
var HTMLupdateDate = '<div class="row">%date%</div>';

var HTMLvalueBox = '<div id="%id%" class="row reading-group"><div class="row reading-name">%description%</div></div>';
var HTMLvalue = '<div class="row reading-value">%value%<span class="reading-unit"> %unit%</span></div>';

