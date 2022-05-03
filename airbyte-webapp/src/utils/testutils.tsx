import { act, Queries, queries, render as rtlRender, RenderOptions, RenderResult } from "@testing-library/react";
import React from "react";
import { IntlProvider } from "react-intl";
import { MemoryRouter } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { configContext, defaultConfig } from "config";
import { FeatureService } from "hooks/services/Feature";
import en from "locales/en.json";

type WrapperProps = {
  children?: React.ReactElement;
};

export async function render<
  Q extends Queries = typeof queries,
  Container extends Element | DocumentFragment = HTMLElement
>(ui: React.ReactNode, renderOptions?: RenderOptions<Q, Container>): Promise<RenderResult<Q, Container>> {
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

  let renderResult: RenderResult<Q, Container>;
  await act(async () => {
    renderResult = await rtlRender<Q, Container>(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
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
