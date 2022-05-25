import React, { Suspense } from "react";
import { IntlProvider } from "react-intl";
import { BrowserRouter as Router } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { ApiServices } from "core/ApiServices";
import { ServicesProvider } from "core/servicesProvider";
import { ConfirmationModalService } from "hooks/services/ConfirmationModal";
import { FeatureService } from "hooks/services/Feature";
import { FormChangeTrackerService } from "hooks/services/FormChangeTracker";
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

const I18NProvider: React.FC = ({ children }) => (
  <IntlProvider
    locale="en"
    messages={en}
    defaultRichTextElements={{
      b: (chunk) => <strong>{chunk}</strong>,
    }}
  >
    {children}
  </IntlProvider>
);

const configProviders: ValueProvider<Config> = [envConfigProvider, windowConfigProvider];

const Services: React.FC = ({ children }) => (
  <AnalyticsProvider>
    <ApiErrorBoundary>
      <WorkspaceServiceProvider>
        <FeatureService>
          <NotificationService>
            <ConfirmationModalService>
              <FormChangeTrackerService>
                <ApiServices>{children}</ApiServices>
              </FormChangeTrackerService>
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
        <I18NProvider>
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
        </I18NProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default App;
