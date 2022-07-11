import { json } from "d3";

function convertTZ(date, tzString) {
  console.log(tzString);
  const dd = new Date(
    (typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", {
      timeZone: tzString,
    })
  );
  console.log(dd);
  return dd;
}

function parseData(parse) {
  return function (d) {
    console.log(d.timestamp);

    d.date = convertTZ(parse(d.timestamp), "America/New_York");
    console.log("CVRT", convertTZ(d.date, "America/New_York"));
    console.log(d.date);
    d.timestamp = +d.timestamp;
    d.open = +d.open;
    d.high = +d.high;
    d.low = +d.low;
    d.close = +d.close;
    d.volume = +d.volume;
    d.true_vwap = +d.true_vwap;
    d.vwap = +d.vwap;

    return d;
  };
}

export function getData(chartParams) {
  var promiseOHLC = json(
    `/api/chart?ticker=${encodeURI(chartParams.ticker)}&from=${encodeURI(
      chartParams.from
    )}&to=${encodeURI(chartParams.to)}&res=${encodeURI(
      chartParams.res
    )}&ah=${encodeURI(chartParams.ah)}`
  ).then((data) => {
    return data.chart.map(parseData((d) => new Date(+d)));
  });
  return promiseOHLC;
}
