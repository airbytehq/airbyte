import { GoogleOAuthProvider } from "@react-oauth/google";
import React, { Suspense } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { ApiServices } from "core/ApiServices";
import { AuthContextProvider } from "core/AuthContext";
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
  <AuthContextProvider>
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
  </AuthContextProvider>
);

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <StoreProvider>
          <ServicesProvider>
            <Suspense fallback={<LoadingPage />}>
              <ConfigServiceProvider defaultConfig={defaultConfig} providers={configProviders}>
                <Router>
                  <I18nProvider>
                    <Services>
                      <GoogleOAuthProvider clientId="797465575128-he9j9jrtastc66su472tnv3uvbtkllid.apps.googleusercontent.com">
                        <Routing />
                      </GoogleOAuthProvider>
                    </Services>
                  </I18nProvider>
                </Router>
              </ConfigServiceProvider>
            </Suspense>
          </ServicesProvider>
        </StoreProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default App;
