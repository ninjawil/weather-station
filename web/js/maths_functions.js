//
// maths.js
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

