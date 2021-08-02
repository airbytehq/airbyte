import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";

import en from "locales/en.json";
import cloudLocales from "./locales/en.json";
import GlobalStyle from "global-styles";
import { theme } from "./theme";

import "packages/cloud/config/firebase";

import { Routing } from "./routes";
import LoadingPage from "components/LoadingPage";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import NotificationService from "components/hooks/services/Notification";
import { AnalyticsInitializer } from "views/common/AnalyticsInitializer";
import { AuthenticationProvider } from "./services/auth/AuthService";
import { WorkspaceServiceProvider } from "./services/workspaces/WorkspacesService";

const messages = Object.assign({}, en, cloudLocales);

const customerIdProvider = () => {
  return "";
};

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <IntlProvider locale="en" messages={messages}>
          <CacheProvider>
            <Suspense fallback={<LoadingPage />}>
              <ApiErrorBoundary>
                <NotificationService>
                  <AuthenticationProvider>
                    <AnalyticsInitializer
                      customerIdProvider={customerIdProvider}
                    >
                      <WorkspaceServiceProvider>
                        <Routing />
                      </WorkspaceServiceProvider>
                    </AnalyticsInitializer>
                  </AuthenticationProvider>
                </NotificationService>
              </ApiErrorBoundary>
            </Suspense>
          </CacheProvider>
        </IntlProvider>
      </ThemeProvider>
    </React.StrictMode>
  );
};

export default App;
