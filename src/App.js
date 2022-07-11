import React, { useState } from "react";

import ChartForm from "./components/ChartForm";
import ChartViewer from "./components/ChartViewer";
import "./App.css";

function App() {
  const [chartParams, setChartParams] = useState({
    ticker: "AAPL",
    from: "2020-01-01",
    to: "2020-01-02",
    res: "5m",
    ah: false,
    indicators: true,
  });

  const chartRequestHandler = (chartRequest) => {
    // const chartRequestData = {
    //   ...chartRequest
    // }
    setChartParams(chartRequest);
    console.log("APP", chartRequest);
  };

  return (
    <div className="App">
      <header className="App-header">
        <ChartForm onChartRequest={chartRequestHandler} />
      </header>
      <div className="App-body">
        <ChartViewer chartParams={chartParams} />
      </div>
    </div>
  );
}

export default App;
