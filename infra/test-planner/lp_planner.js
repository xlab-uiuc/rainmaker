function result_obj2(){
  const fs = require('fs');
  let rawdata = fs.readFileSync('obj2.json');
  let model = JSON.parse(rawdata);

  var solver = require("./node_modules/javascript-lp-solver/src/solver"), 
  results;
  results = solver.Solve(model);
  // console.log(results);
  let data = JSON.stringify(results);
  var data_str = JSON.parse(data);

  fs.writeFileSync('obj2-result.json', data);
  return data_str.result
}

module.exports.init = function(){
  console.log(result_obj2());
}
