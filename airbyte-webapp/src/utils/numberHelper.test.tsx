import { render, screen } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import { formatBytes } from "./numberHelper";
import * as en from "../locales/en.json";

const _render = (args: Parameters<typeof formatBytes>) =>
  render(
    <IntlProvider locale="en" messages={en}>
      <div data-testid="test">{formatBytes(...args)}</div>
    </IntlProvider>
  );

describe("#formatBytes", () => {
  const cases: Array<[number | undefined, string]> = [
    [undefined, "0 Bytes"],
    [0, "0 Bytes"],
    [-1, "0 Bytes"],
    [12, "12 Bytes"],
    [1024 * 1 + 1, "1 KB"],
    [1024 * 10 + 1, "10 KB"],
    [1024 * 1024 + 1, "1 MB"],
    [1024 * 1024 * 10 + 1, "10 MB"],
    [1024 * 1024 * 1024 + 1, "1 GB"],
    [1024 * 1024 * 1024 * 10 + 1, "10 GB"],
    [1024 * 1024 * 1024 * 1024 + 1, "1 TB"],
    [1024 * 1024 * 1024 * 1024 * 10 + 1, "10 TB"],
  ];

  it.each(cases)("formats %p as %p", (number, string) => {
    _render([number]);
    const el = screen.getByTestId("test");
    expect(el).toHaveTextContent(string);
  });
});
