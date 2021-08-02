import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";

import en from "locales/en.json";
import GlobalStyle from "global-styles";
import { theme } from "theme";

import "packages/cloud/config/firebase";

import { Routing } from "./routes";
import LoadingPage from "components/LoadingPage";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import NotificationService from "components/hooks/services/Notification";
import { AnalyticsInitializer } from "views/common/AnalyticsInitializer";
import { AuthenticationProvider } from "./services/auth/AuthService";

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <IntlProvider locale="en" messages={en}>
          <CacheProvider>
            <Suspense fallback={<LoadingPage />}>
              <ApiErrorBoundary>
                <NotificationService>
                  <AnalyticsInitializer>
                    <AuthenticationProvider>
                      <Routing />
                    </AuthenticationProvider>
                  </AnalyticsInitializer>
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
