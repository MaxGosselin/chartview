import React from "react";
import PropTypes from "prop-types";

import { format } from "d3-format";
import { timeFormat } from "d3-time-format";

import { ChartCanvas, Chart } from "react-stockcharts";
import {
  BarSeries,
  AreaSeries,
  CandlestickSeries,
  LineSeries,
} from "react-stockcharts/lib/series";
import { XAxis, YAxis } from "react-stockcharts/lib/axes";
import {
  CrossHairCursor,
  CurrentCoordinate,
  MouseCoordinateX,
  MouseCoordinateY,
} from "react-stockcharts/lib/coordinates";

import { discontinuousTimeScaleProvider } from "react-stockcharts/lib/scale";
import {
  OHLCTooltip,
  MovingAverageTooltip,
} from "react-stockcharts/lib/tooltip";
import { ema, wma, sma, tma } from "react-stockcharts/lib/indicator";
import { fitDimensions } from "react-stockcharts/lib/helper";
import { last } from "react-stockcharts/lib/utils";

class CandleStickChartWithMA extends React.Component {
  render() {
    const ema20 = ema()
      .options({
        windowSize: 20, // optional will default to 10
        sourcePath: "close", // optional will default to close as the source
      })
      .skipUndefined(true) // defaults to true
      .merge((d, c) => {
        d.ema20 = c;
      }) // Required, if not provided, log a error
      .accessor((d) => d.ema20) // Required, if not provided, log an error during calculation
      .stroke("blue"); // Optional

    const sma10 = sma()
      .options({ windowSize: 10 })
      .merge((d, c) => {
        d.sma10 = c;
      })
      .accessor((d) => d.sma10)
      .stroke("magenta");

    const sma20 = sma()
      .options({ windowSize: 20 })
      .merge((d, c) => {
        d.sma20 = c;
      })
      .accessor((d) => d.sma20)
      .stroke("yellow");

    const sma100 = sma()
      .options({ windowSize: 100 })
      .merge((d, c) => {
        d.sma100 = c;
      })
      .accessor((d) => d.sma100)
      .stroke("#0154d4");

    const sma200 = ema()
      .options({ windowSize: 200 })
      .merge((d, c) => {
        d.sma200 = c;
      })
      .accessor((d) => d.sma200)
      .stroke("white");

    const ema50 = ema()
      .options({ windowSize: 50 })
      .merge((d, c) => {
        d.ema50 = c;
      })
      .accessor((d) => d.ema50);

    const smaVolume50 = sma()
      .options({ windowSize: 20, sourcePath: "volume" })
      .merge((d, c) => {
        d.smaVolume50 = c;
      })
      .accessor((d) => d.smaVolume50)
      .stroke("#4682B4")
      .fill("#4682B4");

    const vwap = sma()
      .options({ windowSize: 1, sourcePath: "vwap" })
      .merge((d, c) => {
        d.vwap = c;
      })
      .accessor((d) => d.vwap)
      .stroke("orange");

    console.log(this.props);
    const {
      type,
      data: initialData,
      width,
      ratio,
      ticker,
      chart_height,
    } = this.props;

    const calculatedData = ema20(
      sma10(sma20(sma100(sma200(ema50(smaVolume50(vwap(initialData)))))))
    );
    const xScaleProvider = discontinuousTimeScaleProvider.inputDateAccessor(
      (d) => d.date
    );
    const { data, xScale, xAccessor, displayXAccessor } =
      xScaleProvider(calculatedData);

    const start = xAccessor(last(data));
    const end = xAccessor(data[Math.max(0, data.length - 150)]);
    const xExtents = [start, end];

    return (
      <ChartCanvas
        height={chart_height}
        width={width}
        ratio={ratio}
        margin={{ left: 70, right: 70, top: 10, bottom: 30 }}
        type={type}
        seriesName={ticker}
        data={data}
        xScale={xScale}
        xAccessor={xAccessor}
        displayXAccessor={displayXAccessor}
        xExtents={xExtents}
      >
        <Chart
          id={1}
          yExtents={[
            (d) => [d.high, d.low],
            sma10.accessor(),
            sma20.accessor(),
            sma100.accessor(),
            sma200.accessor(),
            ema20.accessor(),
            ema50.accessor(),
            vwap.accessor(),
          ]}
          padding={{ top: 10, bottom: 20 }}
        >
          <XAxis axisAt="bottom" orient="bottom" tickStroke="#FFFFFF" />
          <YAxis
            axisAt="right"
            orient="right"
            tickStroke="#FFFFFF"
            ticks={10}
          />

          <MouseCoordinateY
            at="right"
            orient="right"
            displayFormat={format(".2f")}
          />

          <CandlestickSeries
            stroke={(d) => (d.close > d.open ? "#d40201" : "#2cc900")}
            fill={(d) => (d.close > d.open ? "#d40201" : "#2cc900")}
            wickStroke={(d) => (d.close > d.open ? "#d40201" : "#2cc900")}
          />
          <LineSeries yAccessor={sma10.accessor()} stroke={sma10.stroke()} />
          <LineSeries yAccessor={sma20.accessor()} stroke={sma20.stroke()} />
          <LineSeries yAccessor={sma100.accessor()} stroke={sma100.stroke()} />
          <LineSeries yAccessor={sma200.accessor()} stroke={sma200.stroke()} />
          {/* <LineSeries yAccessor={ema20.accessor()} stroke={ema20.stroke()} />
          <LineSeries yAccessor={ema50.accessor()} stroke={ema50.stroke()} /> */}
          <LineSeries yAccessor={vwap.accessor()} stroke={vwap.stroke()} />
          <CurrentCoordinate
            yAccessor={sma10.accessor()}
            fill={sma10.stroke()}
          />
          <CurrentCoordinate
            yAccessor={sma20.accessor()}
            fill={sma20.stroke()}
          />
          <CurrentCoordinate
            yAccessor={sma100.accessor()}
            fill={sma100.stroke()}
          />
          <CurrentCoordinate
            yAccessor={sma200.accessor()}
            fill={sma200.stroke()}
          />
          {/* <CurrentCoordinate
            yAccessor={ema20.accessor()}
            fill={ema20.stroke()}
          />
          <CurrentCoordinate
            yAccessor={ema50.accessor()}
            fill={ema50.stroke()}
          /> */}
          <CurrentCoordinate yAccessor={vwap.accessor()} fill={vwap.stroke()} />
          <OHLCTooltip
            origin={[-40, 0]}
            textFill={"#ffffff"}
            labelFill={"#01d3d4"}
          />
          <MovingAverageTooltip
            textFill={"#ffffff"}
            labelFill={"#01d3d4"}
            // fontSize={14}
            onClick={(e) => console.log(e)}
            origin={[-38, 15]}
            options={[
              {
                yAccessor: sma10.accessor(),
                type: "MA",
                stroke: sma10.stroke(),
                windowSize: sma10.options().windowSize,
                echo: "some echo here",
              },
              {
                yAccessor: sma20.accessor(),
                type: "MA",
                stroke: sma20.stroke(),
                windowSize: sma20.options().windowSize,
                echo: "some echo here",
              },
              {
                yAccessor: sma100.accessor(),
                type: "MA",
                stroke: sma100.stroke(),
                windowSize: sma100.options().windowSize,
                echo: "some echo here",
              },
              {
                yAccessor: sma200.accessor(),
                type: "MA",
                stroke: sma200.stroke(),
                windowSize: sma200.options().windowSize,
                echo: "some echo here",
              },
              // {
              //   yAccessor: ema20.accessor(),
              //   type: "EMA",
              //   stroke: ema20.stroke(),
              //   windowSize: ema20.options().windowSize,
              //   echo: "some echo here",
              // },
              // {
              //   yAccessor: ema50.accessor(),
              //   type: "EMA",
              //   stroke: ema50.stroke(),
              //   windowSize: ema50.options().windowSize,
              //   echo: "some echo here",
              // },
              {
                yAccessor: vwap.accessor(),
                type: "VWAP",
                stroke: vwap.stroke(),
                windowSize: vwap.options().windowSize,
                echo: "some echo here",
              },
            ]}
          />
        </Chart>
        <Chart
          id={2}
          yExtents={[(d) => d.volume, smaVolume50.accessor()]}
          height={chart_height * 0.15}
          origin={(w, h) => [0, h - chart_height * 0.15]}
        >
          <YAxis
            axisAt="left"
            orient="left"
            ticks={5}
            tickFormat={format(".2s")}
          />

          <MouseCoordinateX
            at="bottom"
            orient="bottom"
            displayFormat={timeFormat("%Y-%m-%d")}
          />
          <MouseCoordinateY
            at="left"
            orient="left"
            displayFormat={format(".4s")}
          />

          <BarSeries
            yAccessor={(d) => d.volume}
            stroke={(d) => (d.close > d.open ? "#d40201" : "#2cc900")}
            fill={(d) => (d.close > d.open ? "#d40201" : "#2cc900")}
          />
          <AreaSeries
            yAccessor={smaVolume50.accessor()}
            stroke={smaVolume50.stroke()}
            fill={smaVolume50.fill()}
          />
          <CurrentCoordinate
            yAccessor={smaVolume50.accessor()}
            fill={smaVolume50.stroke()}
          />
          <CurrentCoordinate yAccessor={(d) => d.volume} fill="#9B0A47" />
        </Chart>
        <CrossHairCursor stroke="#FFFFFF" />
      </ChartCanvas>
    );
  }
}

CandleStickChartWithMA.propTypes = {
  data: PropTypes.array.isRequired,
  width: PropTypes.number.isRequired,
  ratio: PropTypes.number.isRequired,
  type: PropTypes.oneOf(["svg", "hybrid"]).isRequired,
};

CandleStickChartWithMA.defaultProps = {
  type: "svg",
};
CandleStickChartWithMA = fitDimensions(CandleStickChartWithMA);

export default CandleStickChartWithMA;
