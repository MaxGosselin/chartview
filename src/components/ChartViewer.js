import React from "react";
import "./ChartViewer.css";
import Chart from "./Chart";
import { getData } from "./utils";
// import { TypeChooser } from "react-stockcharts/lib/helper";

class ChartViewer extends React.Component {
  state = {
    data: null,
    prevPropsParams: this.props.chartParams,
    heigh: 600,
  };
  componentDidMount() {
    getData(this.props.chartParams).then((data) => {
      console.log(data);
      this.setState({ data });
    });
    const height = this.divElement.clientHeight - 50;
    this.setState({ height });
    console.log("PROPS", this.props);
  }
  componentDidUpdate() {
    if (this.state.prevPropsParams !== this.props.chartParams) {
      console.log("STATE", this.state);
      console.log("PROPS", this.props);
      const height = this.divElement.clientHeight;
      getData(this.props.chartParams).then((ohlc) => {
        // console.log(ohlc);
        this.setState({
          data: ohlc,
          prevPropsParams: this.props.chartParams,
          height: height,
        });
      });
    }
  }
  //   handleChartChange = (event) => {

  //     this.setState({ data: getData(this.props.chartParams) });
  //   };
  render() {
    if (this.state.data == null) {
      return (
        <div
          className="cv__chart-container"
          ref={(divElement) => {
            this.divElement = divElement;
          }}
        >
          <p>Request a chart!</p>
        </div>
      );
    }
    return (
      <div
        className="cv__chart-container"
        ref={(divElement) => {
          this.divElement = divElement;
        }}
      >
        <Chart
          //   onChange={this.handleChartChange}
          type={"svg"}
          data={this.state.data}
          ratio={2}
          ticker={this.props.chartParams.ticker}
          chart_height={this.state.height}
          indicators={this.props.chartParams.indicators}
          vwap_show={this.props.chartParams.vwap_show}
        />
      </div>
    );
  }
}

export default ChartViewer;
