import React from "react";

import { MemoryRouter } from "react-router-dom";
import { IntlProvider } from "react-intl";
import { ThemeProvider } from "styled-components";
import { QueryClientProvider, QueryClient } from "react-query";

// TODO: theme was not working correctly so imported directly
import { theme } from "../src/theme";
import messages from "../src/locales/en.json";
import { FeatureService } from "../src/hooks/services/Feature";
import { ConfigServiceProvider, config } from "../src/config";
import { DocumentationPanelProvider } from "../src/views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ServicesProvider } from "../src/core/servicesProvider";
import { analyticsServiceContext } from "../src/hooks/services/Analytics";
import { AppMonitoringServiceProvider } from "../src/hooks/services/AppMonitoringService";
import type { AnalyticsService } from "../src/core/analytics";

const analyticsContextMock: AnalyticsService = {
    track: () => {},
    setContext: () => {},
    removeFromContext: () => {},
} as unknown as AnalyticsService;

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
    <analyticsServiceContext.Provider value={analyticsContextMock}>
      <QueryClientProvider client={queryClient}>
        <ServicesProvider>
          <MemoryRouter>
            <IntlProvider messages={messages} locale={"en"}>
              <ThemeProvider theme={theme}>
                <ConfigServiceProvider config={config}>
                  <DocumentationPanelProvider>
                    <AppMonitoringServiceProvider>
                      <FeatureService features={[]}>
                        {getStory()}
                      </FeatureService>
                    </AppMonitoringServiceProvider>
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
