import React from "react";
import { render as rtlRender, RenderResult } from "@testing-library/react";
import { ThemeProvider } from "styled-components";
import { History } from "history";
import { MemoryRouter } from "react-router-dom";
import { IntlProvider } from "react-intl";

import en from "locales/en.json";
import { FeatureService } from "hooks/services/Feature";
import { configContext, defaultConfig } from "config";

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
      <TestWrapper>
        <configContext.Provider value={{ config: defaultConfig }}>
          <FeatureService>
            <MemoryRouter>{children}</MemoryRouter>
          </FeatureService>
        </configContext.Provider>
      </TestWrapper>
    );
  }

  return rtlRender(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
}

export const TestWrapper: React.FC = ({ children }) => (
  <ThemeProvider theme={{}}>
    <IntlProvider locale="en" messages={en}>
      {children}
    </IntlProvider>
  </ThemeProvider>
);
