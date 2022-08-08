import React from "react";

import { MemoryRouter } from "react-router-dom";
import { IntlProvider } from "react-intl";
import { ThemeProvider } from "styled-components";
import { QueryClientProvider, QueryClient } from "react-query";

// TODO: theme was not working correctly so imported directly
import { theme } from "../src/theme";
import GlobalStyle from "../src/global-styles";
import messages from "../src/locales/en.json";
import { FeatureService } from "../src/hooks/services/Feature";
import { ConfigServiceProvider, defaultConfig } from "../src/config";
import { DocumentationPanelProvider } from "../src/views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ServicesProvider } from "../src/core/servicesProvider";
import { analyticsServiceContext, AnalyticsServiceProviderValue } from "../src/hooks/services/Analytics";

const AnalyticsContextMock: AnalyticsServiceProviderValue = {
  analyticsContext: {},
  setContext: () => {},
  addContextProps: () => {},
  removeContextProps: () => {},
  service: {
    track: () => {},
  },
} as unknown as AnalyticsServiceProviderValue;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      suspense: true,
    },
  },
});

export const withProviders = (getStory) => (
  <React.Suspense fallback={null}>
    <analyticsServiceContext.Provider value={AnalyticsContextMock}>
      <QueryClientProvider client={queryClient}>
        <ServicesProvider>
          <MemoryRouter>
            <IntlProvider messages={messages} locale={"en"}>
              <ThemeProvider theme={theme}>
                <ConfigServiceProvider defaultConfig={defaultConfig} providers={[]}>
                  <DocumentationPanelProvider>
                    <FeatureService features={[]}>
                      <GlobalStyle />
                      {getStory()}
                    </FeatureService>
                  </DocumentationPanelProvider>
                </ConfigServiceProvider>
              </ThemeProvider>
            </IntlProvider>
          </MemoryRouter>
        </ServicesProvider>
      </QueryClientProvider>
    </analyticsServiceContext.Provider>
  </React.Suspense>
);
