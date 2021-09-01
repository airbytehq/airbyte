import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";
import { QueryClient, QueryClientProvider } from "react-query";

import en from "locales/en.json";
import cloudLocales from "packages/cloud/locales/en.json";
import GlobalStyle from "global-styles";
import { theme } from "packages/cloud/theme";

import "packages/cloud/config/firebase";

import { Routing } from "packages/cloud/routes";
import LoadingPage from "components/LoadingPage";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import NotificationServiceProvider from "hooks/services/Notification";
import { AnalyticsInitializer } from "views/common/AnalyticsInitializer";
import { FeatureService } from "hooks/services/Feature";
import { AuthenticationProvider } from "packages/cloud/services/auth/AuthService";
import { ServicesProvider, useApiServices } from "core/servicesProvider";
import { Config, ConfigService, ValueProvider } from "config";
import {
  useCurrentWorkspaceProvider,
  useCustomerIdProvider,
} from "packages/cloud/services";
import {
  envConfigProvider,
  windowConfigProvider,
} from "config/configProviders";
import {
  cloudEnvConfigProvider,
  fileConfigProvider,
} from "packages/cloud/config/configProviders";
import { defaultConfig } from "packages/cloud/config";

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
  cloudEnvConfigProvider,
  windowConfigProvider,
  envConfigProvider,
];

const services = {
  currentWorkspaceProvider: useCurrentWorkspaceProvider,
  useCustomerIdProvider: useCustomerIdProvider,
};

const AppServices: React.FC = ({ children }) => (
  <ServicesProvider inject={services}>
    <ConfigService defaultConfig={defaultConfig} providers={configProviders}>
      <ServiceOverrides />
      {children}
    </ConfigService>
  </ServicesProvider>
);

const ServiceOverrides: React.FC = React.memo(() => {
  useApiServices();
  return null;
});

const App: React.FC = () => (
  <React.StrictMode>
    <StyleProvider>
      <I18NProvider>
        <StoreProvider>
          <Suspense fallback={<LoadingPage />}>
            <ApiErrorBoundary>
              <NotificationServiceProvider>
                <FeatureService>
                  <AppServices>
                    <AuthenticationProvider>
                      <AnalyticsInitializer>
                        <Routing />
                      </AnalyticsInitializer>
                    </AuthenticationProvider>
                  </AppServices>
                </FeatureService>
              </NotificationServiceProvider>
            </ApiErrorBoundary>
          </Suspense>
        </StoreProvider>
      </I18NProvider>
    </StyleProvider>
  </React.StrictMode>
);

export default React.memo(App);
