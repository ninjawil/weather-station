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
// check whether SOME multiple values exist within an Javascript array
//
//  Author: wdf
//
//-------------------------------------------------------------------------------
function containsSome(needles, haystack){ 
  for(var i = 0 , len = needles.length; i < len; i++){
     if($.inArray(needles[i], haystack) !== -1) return true;
  }
  return false;
}