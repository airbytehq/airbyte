import React from "react";
import { render as rtlRender, RenderResult } from "@testing-library/react";
import { History, createMemoryHistory } from "history";
import { Router } from "react-router-dom";
import { IntlProvider } from "react-intl";

import en from "../locales/en.json";

export type RenderOptions = {
  // optionally pass in a history object to control routes in the test
  history?: History;
};

type WrapperProps = {
  children?: React.ReactNode;
};

export function render(
  ui: React.ReactNode,
  renderOptions?: RenderOptions
): RenderResult {
  function Wrapper({ children }: WrapperProps) {
    return (
      <React.StrictMode>
        <IntlProvider locale="en" messages={en}>
          <Router
            history={
              (renderOptions && renderOptions.history) || createMemoryHistory()
            }
          >
            {children}
          </Router>
        </IntlProvider>
      </React.StrictMode>
    );
  }

  return rtlRender(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
}
