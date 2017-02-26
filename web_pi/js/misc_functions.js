//
// misc_functions.js
// Will de Freitas
//
// Maths functions
//


//-------------------------------------------------------------------------------
// 	Standard Deviation
//
//	Author: derickbailey
// 	Site:	https://gist.github.com/derickbailey/b7c6615ecf1fe9ad60a8
//
//-------------------------------------------------------------------------------
function standardDeviation(values){
  var avg = average(values);
  
  var squareDiffs = values.map(function(value){
    var diff = value - avg;
    var sqrDiff = diff * diff;
    return sqrDiff;
  });
  
  var avgSquareDiff = average(squareDiffs);

  var stdDev = Math.sqrt(avgSquareDiff);
  return stdDev;
}



//-------------------------------------------------------------------------------
// Average
//
//	Author: derickbailey
// 	Site:	https://gist.github.com/derickbailey/b7c6615ecf1fe9ad60a8
//
//-------------------------------------------------------------------------------
function average(data){
  var sum = data.reduce(function(sum, value){
    return sum + value;
  }, 0);

  var avg = sum / data.length;
  return avg;
}




//-------------------------------------------------------------------------------
// check whether ALL multiple values exist within an Javascript array
//
//  Author: ggreiner
//  Site: https://stackoverflow.com/questions/9204283/how-to-check-whether-multiple-values-exist-within-an-javascript-array
//
//
//      containsAll([34, 78, 89], [78, 67, 34, 99, 56, 89]); // true
//      containsAll([34, 78, 89], [78, 67, 99, 56, 89]); // false
//      containsAll([34, 78, 89], [78, 89]); // false
//
//
//-------------------------------------------------------------------------------
function containsAll(needles, haystack){ 
  for(var i = 0 , len = needles.length; i < len; i++){
     if($.inArray(needles[i], haystack) == -1) return false;
  }
  return true;
}


//-------------------------------------------------------------------------------
//  Check whether ANY multiple values exist within an Javascript array
//
//  Author: wdf
//
//-------------------------------------------------------------------------------
function containsAny(needles, haystack){ 
  for(var i = 0 , len = needles.length; i < len; i++){
     if($.inArray(needles[i], haystack) !== -1) return needles[i];
  }
  return false;
}



//-------------------------------------------------------------------------------
//  Finds key from value
//
//  Author: wdf
//
//-------------------------------------------------------------------------------
function findKeyfromValue(value, object){ 
  for(var key in object) {
      if(object[key] === value) return key;
  } 
  return false;
}



//-------------------------------------------------------------------------------
//  Get the ISO week date week number
//
//  Author: wdf
//  Site:   http://techblog.procurios.nl/k/news/view/33796/14863/calculate-iso-8601-week-and-year-in-javascript.html 
//
//-------------------------------------------------------------------------------
Date.prototype.getWeek = function () {  
    // Create a copy of this date object  
    var target  = new Date(this.valueOf());  
  
    // ISO week date weeks start on monday  
    // so correct the day number  
    var dayNr   = (this.getDay() + 6) % 7;  
  
    // ISO 8601 states that week 1 is the week  
    // with the first thursday of that year.  
    // Set the target date to the thursday in the target week  
    target.setDate(target.getDate() - dayNr + 3);  
  
    // Store the millisecond value of the target date  
    var firstThursday = target.valueOf();  
  
    // Set the target to the first thursday of the year  
    // First set the target to january first  
    target.setMonth(0, 1);  
    // Not a thursday? Correct the date to the next thursday  
    if (target.getDay() != 4) {  
        target.setMonth(0, 1 + ((4 - target.getDay()) + 7) % 7);  
    }  
  
    // The weeknumber is the number of weeks between the   
    // first thursday of the year and the thursday in the target week  
    return 1 + Math.ceil((firstThursday - target) / 604800000); // 604800000 = 7 * 24 * 3600 * 1000  
} 



//-------------------------------------------------------------------------------
// Grab data from file
//
//  Author: wdf
//  Site:   
//
//-------------------------------------------------------------------------------
function getFileData(loc, type, functionCall, args) {

    var error_data = {"9999": {"time":10, "msg": "Loading data failure"}};
  
    $.ajax({
        cache: false,
        url: loc,
        dataType: type,
        success: function(config_data) {            
            args.push(config_data);
            functionCall.apply(this, args);
        },
        error: function () {
            displayErrorMessage(error_data, false, false);
        },
        onFailure: function () {
            displayErrorMessage(error_data, false, false);
        }
    });
    
}



//-------------------------------------------------------------------------------
// Return passed object
//
//  Author: 
//  Site:   
//
//-------------------------------------------------------------------------------
function cloneObject(obj) {
    return jQuery.extend(true, {}, obj);
}
