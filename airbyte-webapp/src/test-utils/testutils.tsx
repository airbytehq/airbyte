import { act, Queries, queries, render as rtlRender, RenderOptions, RenderResult } from "@testing-library/react";
import React, { Suspense } from "react";
import { IntlProvider } from "react-intl";
import { QueryClient, QueryClientProvider } from "react-query";
import { MemoryRouter } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { ConfigContext, defaultConfig } from "config";
import { ServicesProvider } from "core/servicesProvider";
import { defaultFeatures, FeatureService } from "hooks/services/Feature";
import en from "locales/en.json";

interface WrapperProps {
  children?: React.ReactElement;
}

export async function render<
  Q extends Queries = typeof queries,
  Container extends Element | DocumentFragment = HTMLElement
>(ui: React.ReactNode, renderOptions?: RenderOptions<Q, Container>): Promise<RenderResult<Q, Container>> {
  const Wrapper = ({ children }: WrapperProps) => {
    const queryClient = new QueryClient();

    return (
      <TestWrapper>
        <ConfigContext.Provider value={{ config: defaultConfig }}>
          <FeatureService features={defaultFeatures}>
            <ServicesProvider>
              <QueryClientProvider client={queryClient}>
                <MemoryRouter>
                  <Suspense fallback={<div>'fallback content'</div>}>{children}</Suspense>
                </MemoryRouter>
              </QueryClientProvider>
            </ServicesProvider>
          </FeatureService>
        </ConfigContext.Provider>
      </TestWrapper>
    );
  };

  let renderResult: RenderResult<Q, Container>;
  await act(async () => {
    renderResult = await rtlRender<Q, Container>(<div>{ui}</div>, { wrapper: Wrapper, ...renderOptions });
  });

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  return renderResult!;
}
export const TestWrapper: React.FC = ({ children }) => (
  <ThemeProvider theme={{}}>
    <IntlProvider locale="en" messages={en} onError={() => null}>
      {children}
    </IntlProvider>
  </ThemeProvider>
);
