import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";

import en from "./locales/en.json";
import GlobalStyle from "./global-styles";
import { theme } from "./theme";

import { Routing } from "./pages/routes";
import LoadingPage from "./components/LoadingPage";
import ApiErrorBoundary from "./components/ApiErrorBoundary";
import NotificationService from "hooks/services/Notification";
import { AnalyticsInitializer } from "views/common/AnalyticsInitializer";
import {
  useCurrentWorkspace,
  usePickFirstWorkspace,
} from "hooks/services/useWorkspace";
import { Feature, FeatureService } from "hooks/services/Feature";
import { ServicesProvider } from "core/servicesProvider";
import { useApiServices } from "core/defaultServices";
import { envConfigProvider, windowConfigProvider } from "./config";
import {
  Config,
  ConfigServiceProvider,
  defaultConfig,
  ValueProvider,
} from "./config";

function useCustomerIdProvider() {
  const workspace = useCurrentWorkspace();

  return workspace.customerId;
}

const Features: Feature[] = [
  {
    id: "ALLOW_UPLOAD_CUSTOM_IMAGE",
  },
  {
    id: "ALLOW_CUSTOM_DBT",
  },
];

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

const StoreProvider: React.FC = ({ children }) => (
  <CacheProvider>{children}</CacheProvider>
);

const configProviders: ValueProvider<Config> = [
  envConfigProvider,
  windowConfigProvider,
];

const services = {
  currentWorkspaceProvider: usePickFirstWorkspace,
  useCustomerIdProvider: useCustomerIdProvider,
};

const AppServices: React.FC = ({ children }) => (
  <ServicesProvider inject={services}>
    <ConfigServiceProvider
      defaultConfig={defaultConfig}
      providers={configProviders}
    >
      <ServiceOverrides>{children}</ServiceOverrides>
    </ConfigServiceProvider>
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
              <ApiErrorBoundary>
                <FeatureService features={Features}>
                  <NotificationService>
                    <AppServices>
                      <AnalyticsInitializer>
                        <Routing />
                      </AnalyticsInitializer>
                    </AppServices>
                  </NotificationService>
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
