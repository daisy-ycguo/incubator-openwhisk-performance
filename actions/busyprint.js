function main(params) {
  var repeat = params.repeat || 100;
  for (var i=0;i<repeat;i++) {
     console.log(i+": I'm busy.");
  }
  return {};
}
