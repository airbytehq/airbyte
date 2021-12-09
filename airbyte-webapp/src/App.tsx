import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";
import { QueryClient, QueryClientProvider } from "react-query";
import { BrowserRouter as Router } from "react-router-dom";

import en from "./locales/en.json";
import GlobalStyle from "./global-styles";
import { theme } from "./theme";

import { Routing } from "./pages/routes";
import LoadingPage from "./components/LoadingPage";
import ApiErrorBoundary from "./components/ApiErrorBoundary";
import NotificationService from "hooks/services/Notification";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";
import { FeatureService } from "hooks/services/Feature";
import { ServicesProvider } from "core/servicesProvider";
import { useApiServices } from "core/defaultServices";
import {
  Config,
  ConfigServiceProvider,
  defaultConfig,
  envConfigProvider,
  ValueProvider,
  windowConfigProvider,
} from "./config";
import { WorkspaceServiceProvider } from "./services/workspaces/WorkspacesService";

const StyleProvider: React.FC = ({ children }) => (
  <ThemeProvider theme={theme}>
    <GlobalStyle />
    {children}
  </ThemeProvider>
);

const I18NProvider: React.FC = ({ children }) => (
  <IntlProvider locale="en" messages={en}>
    {children}
  </IntlProvider>
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      suspense: true,
    },
  },
});

const StoreProvider: React.FC = ({ children }) => (
  <CacheProvider>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  </CacheProvider>
);

const configProviders: ValueProvider<Config> = [
  envConfigProvider,
  windowConfigProvider,
];

const ServiceOverrides: React.FC = React.memo(({ children }) => {
  useApiServices();
  return <>{children}</>;
});

const Services: React.FC = ({ children }) => (
  <ConfigServiceProvider
    defaultConfig={defaultConfig}
    providers={configProviders}
  >
    <AnalyticsProvider>
      <ApiErrorBoundary>
        <WorkspaceServiceProvider>
          <FeatureService>
            <NotificationService>
              <ServicesProvider>
                <ServiceOverrides>{children}</ServiceOverrides>
              </ServicesProvider>
            </NotificationService>
          </FeatureService>
        </WorkspaceServiceProvider>
      </ApiErrorBoundary>
    </AnalyticsProvider>
  </ConfigServiceProvider>
);

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <I18NProvider>
          <Router>
            <StoreProvider>
              <Suspense fallback={<LoadingPage />}>
                <Services>
                  <Routing />
                </Services>
              </Suspense>
            </StoreProvider>
          </Router>
        </I18NProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default App;
