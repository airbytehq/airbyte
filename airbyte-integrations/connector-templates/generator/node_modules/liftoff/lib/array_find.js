'use strict';

function arrayFind(arr, fn) {
  if (!Array.isArray(arr)) {
    return;
  }

  var idx = 0;
  while (idx < arr.length) {
    var result = fn(arr[idx]);
    if (result) {
      return result;
    }
    idx++;
  }
}

module.exports = arrayFind;
