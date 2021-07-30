import React from "react";
import ReactDOM from "react-dom";

import CloudApp from "packages/cloud/App";
import App from "./App";

if (process.env.REACT_APP_CLOUD) {
  ReactDOM.render(<CloudApp />, document.getElementById("root"));
} else {
  ReactDOM.render(<App />, document.getElementById("root"));
}
