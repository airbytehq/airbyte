import { act, Queries, render as rtlRender, RenderResult } from "@testing-library/react";
import { History } from "history";
import React from "react";
import { IntlProvider } from "react-intl";
import { MemoryRouter } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { configContext, defaultConfig } from "config";
import { FeatureService } from "hooks/services/Feature";
import en from "locales/en.json";

export type RenderOptions = {
  // optionally pass in a history object to control routes in the test
  history?: History;
  container?: HTMLElement;
};

type WrapperProps = {
  children?: React.ReactNode;
};

export async function render(
  ui: React.ReactNode,
  renderOptions?: RenderOptions
): Promise<RenderResult<Queries, HTMLElement>> {
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

  let renderResult: RenderResult<Queries, HTMLElement>;
  await act(async () => {
    renderResult = await rtlRender(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
  });

  return renderResult!;
}

export const TestWrapper: React.FC = ({ children }) => (
  <ThemeProvider theme={{}}>
    <IntlProvider locale="en" messages={en}>
      {children}
    </IntlProvider>
  </ThemeProvider>
);
