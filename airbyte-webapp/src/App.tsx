import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";
import { QueryClient, QueryClientProvider } from "react-query";

import en from "./locales/en.json";
import GlobalStyle from "./global-styles";
import { theme } from "./theme";

import { Routing } from "./pages/routes";
import LoadingPage from "./components/LoadingPage";
import ApiErrorBoundary from "./components/ApiErrorBoundary";
import NotificationService from "hooks/services/Notification";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";
import { usePickFirstWorkspace } from "hooks/services/useWorkspace";
import { FeatureService } from "hooks/services/Feature";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
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

const queryClient = new QueryClient();

const StoreProvider: React.FC = ({ children }) => (
  <CacheProvider>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  </CacheProvider>
);

const configProviders: ValueProvider<Config> = [
  envConfigProvider,
  windowConfigProvider,
];

const services = {
  currentWorkspaceProvider: usePickFirstWorkspace,
};

const AppServices: React.FC = ({ children }) => (
  <ServicesProvider inject={services}>
    <ServiceOverrides>{children}</ServiceOverrides>
  </ServicesProvider>
);

const ServiceOverrides: React.FC = React.memo(({ children }) => {
  useApiServices();
  return <>{children}</>;
});

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <I18NProvider>
          <StoreProvider>
            <Suspense fallback={<LoadingPage />}>
              <ConfigServiceProvider
                defaultConfig={defaultConfig}
                providers={configProviders}
              >
                <AnalyticsProvider>
                  <ApiErrorBoundary>
                    <FeatureService>
                      <NotificationService>
                        <AppServices>
                          <OnboardingServiceProvider>
                            <Routing />
                          </OnboardingServiceProvider>
                        </AppServices>
                      </NotificationService>
                    </FeatureService>
                  </ApiErrorBoundary>
                </AnalyticsProvider>
              </ConfigServiceProvider>
            </Suspense>
          </StoreProvider>
        </I18NProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default App;
