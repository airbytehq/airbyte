import React, { Suspense } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { ApiServices } from "core/ApiServices";
import { I18nProvider } from "core/i18n";
import { ServicesProvider } from "core/servicesProvider";
import { ConfirmationModalService } from "hooks/services/ConfirmationModal";
import { defaultFeatures, FeatureService } from "hooks/services/Feature";
import { FormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { ModalServiceProvider } from "hooks/services/Modal";
import NotificationService from "hooks/services/Notification";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";
import { StoreProvider } from "views/common/StoreProvider";

import ApiErrorBoundary from "./components/ApiErrorBoundary";
import LoadingPage from "./components/LoadingPage";
import {
  Config,
  ConfigServiceProvider,
  defaultConfig,
  envConfigProvider,
  ValueProvider,
  windowConfigProvider,
} from "./config";
import GlobalStyle from "./global-styles";
import en from "./locales/en.json";
import { Routing } from "./pages/routes";
import { WorkspaceServiceProvider } from "./services/workspaces/WorkspacesService";
import { theme } from "./theme";

const StyleProvider: React.FC = ({ children }) => (
  <ThemeProvider theme={theme}>
    <GlobalStyle />
    {children}
  </ThemeProvider>
);

const configProviders: ValueProvider<Config> = [envConfigProvider, windowConfigProvider];

const Services: React.FC = ({ children }) => (
  <AnalyticsProvider>
    <ApiErrorBoundary>
      <WorkspaceServiceProvider>
        <FeatureService features={defaultFeatures}>
          <NotificationService>
            <ConfirmationModalService>
              <ModalServiceProvider>
                <FormChangeTrackerService>
                  <ApiServices>{children}</ApiServices>
                </FormChangeTrackerService>
              </ModalServiceProvider>
            </ConfirmationModalService>
          </NotificationService>
        </FeatureService>
      </WorkspaceServiceProvider>
    </ApiErrorBoundary>
  </AnalyticsProvider>
);

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <I18nProvider locale="en" messages={en}>
          <StoreProvider>
            <ServicesProvider>
              <Suspense fallback={<LoadingPage />}>
                <ConfigServiceProvider defaultConfig={defaultConfig} providers={configProviders}>
                  <Router>
                    <Services>
                      <Routing />
                    </Services>
                  </Router>
                </ConfigServiceProvider>
              </Suspense>
            </ServicesProvider>
          </StoreProvider>
        </I18nProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default App;
