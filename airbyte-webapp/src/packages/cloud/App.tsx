import React, { Suspense } from "react";
import { HelmetProvider } from "react-helmet-async";
import { BrowserRouter as Router } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import { ApiErrorBoundary } from "components/common/ApiErrorBoundary";
import LoadingPage from "components/LoadingPage";

import { ConfigServiceProvider, config } from "config";
import { I18nProvider } from "core/i18n";
import { AppMonitoringServiceProvider } from "hooks/services/AppMonitoringService";
import { ConfirmationModalService } from "hooks/services/ConfirmationModal";
import { defaultCloudFeatures, FeatureService } from "hooks/services/Feature";
import { FormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { ModalServiceProvider } from "hooks/services/Modal";
import { NotificationService } from "hooks/services/Notification";
import en from "locales/en.json";
import { Routing } from "packages/cloud/cloudRoutes";
import cloudLocales from "packages/cloud/locales/en.json";
import { AuthenticationProvider } from "packages/cloud/services/auth/AuthService";
import { theme } from "packages/cloud/theme";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";
import { StoreProvider } from "views/common/StoreProvider";

import { AppServicesProvider } from "./services/AppServicesProvider";
import { IntercomProvider } from "./services/thirdParty/intercom/IntercomProvider";

const messages = { ...en, ...cloudLocales };

const StyleProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

const Services: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <AnalyticsProvider>
    <AppMonitoringServiceProvider>
      <ApiErrorBoundary>
        <NotificationService>
          <ConfirmationModalService>
            <ModalServiceProvider>
              <FormChangeTrackerService>
                <FeatureService features={defaultCloudFeatures}>
                  <AppServicesProvider>
                    <AuthenticationProvider>
                      <HelmetProvider>
                        <IntercomProvider>{children}</IntercomProvider>
                      </HelmetProvider>
                    </AuthenticationProvider>
                  </AppServicesProvider>
                </FeatureService>
              </FormChangeTrackerService>
            </ModalServiceProvider>
          </ConfirmationModalService>
        </NotificationService>
      </ApiErrorBoundary>
    </AppMonitoringServiceProvider>
  </AnalyticsProvider>
);

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <I18nProvider locale="en" messages={messages}>
          <StoreProvider>
            <Suspense fallback={<LoadingPage />}>
              <ConfigServiceProvider config={config}>
                <Router>
                  <Services>
                    <Routing />
                  </Services>
                </Router>
              </ConfigServiceProvider>
            </Suspense>
          </StoreProvider>
        </I18nProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default React.memo(App);
