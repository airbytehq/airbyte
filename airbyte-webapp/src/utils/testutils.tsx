import React from "react";
import { render as rtlRender, RenderResult } from "@testing-library/react";
import { ThemeProvider } from "styled-components";
import { History, createMemoryHistory } from "history";
import { Router } from "react-router-dom";
import { IntlProvider } from "react-intl";

import en from "locales/en.json";
import { FeatureService } from "hooks/services/Feature";
import { ConfigServiceProvider, defaultConfig } from "config";

export type RenderOptions = {
  // optionally pass in a history object to control routes in the test
  history?: History;
  container?: HTMLElement;
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
      <ThemeProvider theme={{}}>
        <IntlProvider locale="en" messages={en}>
          <ConfigServiceProvider defaultConfig={defaultConfig} providers={[]}>
            <FeatureService>
              <Router
                history={
                  (renderOptions && renderOptions.history) ||
                  createMemoryHistory()
                }
              >
                {children}
              </Router>
            </FeatureService>
          </ConfigServiceProvider>
        </IntlProvider>
      </ThemeProvider>
    );
  }

  return rtlRender(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
}
