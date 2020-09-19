import React from "react";
import ReactDOM from "react-dom";

import App from "./App";

test("renders react app", () => {
  const div = document.createElement("div");
  ReactDOM.render(<App />, div);
});
