import React, { useState } from "react";

import "./ChartForm.css";

const ChartForm = (props) => {
  const submitHandler = (event) => {
    event.preventDefault();
    const chartData = formInput;

    props.onChartRequest(chartData);
  };

  const [formInput, setFormInput] = useState({
    ticker: "AAPL",
    from: "2020-01-01",
    to: "2020-01-02",
    res: "5m",
    ah: false,
    indicators: true,
    vwap_show: 1,
  });

  const tickerChangeHandler = (event) => {
    setFormInput((prevState) => {
      return { ...prevState, ticker: event.target.value };
    });
  };
  const fromChangeHandler = (event) => {
    setFormInput((prevState) => {
      return { ...prevState, from: event.target.value };
    });
  };
  const toChangeHandler = (event) => {
    setFormInput((prevState) => {
      return { ...prevState, to: event.target.value };
    });
  };
  const resChangeHandler = (event) => {
    setFormInput((prevState) => {
      return {
        ...prevState,
        res: event.target.value,
        vwap_show: ["1d", "1wk", "1mo"].includes(event.target.value) ? 0 : 1,
      };
    });
  };
  const ahChangeHandler = (event) => {
    setFormInput((prevState) => {
      return { ...prevState, ah: !prevState.ah };
    });
  };
  const indicatorsChangeHandler = (event) => {
    setFormInput((prevState) => {
      return { ...prevState, indicators: !prevState.indicators };
    });
  };
  return (
    <div className="cf__cont">
      <form onSubmit={submitHandler}>
        <div className="cf__controls">
          <div className="cf__control">
            <label className="cf__label">Ticker</label>
            <input
              className="cf__input"
              type="text"
              onChange={tickerChangeHandler}
              value={formInput.ticker}
            />
          </div>
          <div className="cf__control">
            <label className="cf__label">From</label>
            <input
              className="cf__input"
              type="text"
              onChange={fromChangeHandler}
              value={formInput.from}
            />
          </div>
          <div className="cf__control">
            <label className="cf__label">To</label>
            <input
              className="cf__input"
              type="text"
              onChange={toChangeHandler}
              value={formInput.to}
            />
          </div>
          <div className="cf__control">
            <label className="cf__label">
              Resolution
              <select
                className="cf__input"
                onChange={resChangeHandler}
                value={formInput.res}
              >
                <option value="1m">1m</option>
                <option value="5m">5m</option>
                <option value="15m">15m</option>
                <option value="30m">30m</option>
                <option value="1h">1h</option>
                <option value="1d">1d</option>
                <option value="1wk">1wk</option>
                <option value="1mo">1mo</option>
              </select>
            </label>
          </div>
          <div className="cf__control">
            <label className="cf__label">Extended hours</label>
            <input type="checkbox" onChange={ahChangeHandler} />
          </div>
          <div className="cf__control">
            <label className="cf__label">SMA</label>
            <input
              type="radio"
              name="indicators"
              onChange={indicatorsChangeHandler}
              defaultChecked
            />
            <label className="cf__label">EMA</label>
            <input
              type="radio"
              name="indicators"
              onChange={indicatorsChangeHandler}
            />
          </div>
          <input className="cf__control cf__submit" type="submit" value="Go" />
        </div>
      </form>
    </div>
  );
};

export default ChartForm;
