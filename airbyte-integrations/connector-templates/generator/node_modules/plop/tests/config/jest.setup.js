// require("cli-testing-library/extend-expect");

import { configure } from "cli-testing-library";
import "cli-testing-library/extend-expect";

configure({
  asyncUtilTimeout: 2000,
  renderAwaitTime: 1000,
  errorDebounceTimeout: 1000,
});
