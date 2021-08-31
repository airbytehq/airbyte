import React, { Suspense, useMemo } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";
import { QueryClient, QueryClientProvider } from "react-query";

import en from "locales/en.json";
import cloudLocales from "./locales/en.json";
import GlobalStyle from "global-styles";
import { theme } from "./theme";

import "packages/cloud/config/firebase";

import { Routing } from "./routes";
import LoadingPage from "components/LoadingPage";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import NotificationServiceProvider from "hooks/services/Notification";
import { AnalyticsInitializer } from "views/common/AnalyticsInitializer";
import { FeatureService } from "hooks/services/Feature";
import { AuthenticationProvider } from "./services/auth/AuthService";
import {
  ServiceInject,
  ServicesProvider,
  WithService,
} from "core/servicesProvider";
import { Config, ConfigService, defaultConfig, ValueProvider } from "config";
import { useCurrentWorkspaceProvider, useCustomerIdProvider } from "./services";
import {
  envConfigProvider,
  fileConfigProvider,
  windowConfigProvider,
} from "config/configProviders";

const messages = Object.assign({}, en, cloudLocales);

const I18NProvider: React.FC = ({ children }) => (
  <IntlProvider locale="en" messages={messages}>
    {children}
  </IntlProvider>
);

const StyleProvider: React.FC = ({ children }) => (
  <ThemeProvider theme={theme}>
    <GlobalStyle />
    {children}
  </ThemeProvider>
);

const queryClient = new QueryClient();

const StoreProvider: React.FC = ({ children }) => (
  <CacheProvider>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  </CacheProvider>
);

const configProviders: ValueProvider<Config> = [
  fileConfigProvider,
  windowConfigProvider,
  envConfigProvider,
];

const AppServices: React.FC = ({ children }) => (
  <ServicesProvider>
    <ServiceOverrides />
    <ConfigService defaultConfig={defaultConfig} providers={configProviders}>
      <FeatureService>{children}</FeatureService>
    </ConfigService>
  </ServicesProvider>
);

const ServiceOverrides: React.FC = () => {
  const services = useMemo<ServiceInject[]>(
    () => [
      ["currentWorkspaceProvider", useCurrentWorkspaceProvider],
      ["useCustomerIdProvider", useCustomerIdProvider],
    ],
    []
  );
  return <WithService serviceInject={services} />;
};

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <I18NProvider>
          <StoreProvider>
            <Suspense fallback={<LoadingPage />}>
              <ApiErrorBoundary>
                <FeatureService>
                  <AppServices>
                    <NotificationServiceProvider>
                      <AuthenticationProvider>
                        <AnalyticsInitializer>
                          <Routing />
                        </AnalyticsInitializer>
                      </AuthenticationProvider>
                    </NotificationServiceProvider>
                  </AppServices>
                </FeatureService>
              </ApiErrorBoundary>
            </Suspense>
          </StoreProvider>
        </I18NProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default App;
