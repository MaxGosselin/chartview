import { json } from "d3";

function parseData(parse) {
  return function (d) {
    d.date = parse(d.timestamp);
    d.timestamp = +d.timestamp;
    d.open = +d.open;
    d.high = +d.high;
    d.low = +d.low;
    d.close = +d.close;
    d.volume = +d.volume;
    //   console.log(d);
    return d;
  };
}

export function getData(chartParams) {
  var promiseOHLC = json(
    `/api/chart?ticker=${encodeURI(chartParams.ticker)}&from=${encodeURI(
      chartParams.from
    )}&to=${encodeURI(chartParams.to)}&res=${encodeURI(chartParams.res)}`
  ).then((data) => {
    return data.chart.map(parseData((d) => new Date(+d)));
  });
  return promiseOHLC;
}
