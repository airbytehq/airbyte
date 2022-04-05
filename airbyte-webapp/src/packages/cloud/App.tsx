import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { BrowserRouter as Router } from "react-router-dom";

import en from "locales/en.json";
import cloudLocales from "packages/cloud/locales/en.json";
import GlobalStyle from "global-styles";
import { theme } from "packages/cloud/theme";

import { Routing } from "packages/cloud/cloudRoutes";
import LoadingPage from "components/LoadingPage";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import NotificationServiceProvider from "hooks/services/Notification";
import { AnalyticsProvider } from "views/common/AnalyticsProvider";
import { FeatureService } from "hooks/services/Feature";
import { AuthenticationProvider } from "packages/cloud/services/auth/AuthService";
import { AppServicesProvider } from "./services/AppServicesProvider";
import { IntercomProvider } from "./services/thirdParty/intercom/IntercomProvider";
import { ConfigProvider } from "./services/ConfigProvider";
import { StoreProvider } from "views/common/StoreProvider";

const messages = Object.assign({}, en, cloudLocales);

const I18NProvider: React.FC = ({ children }) => (
  <IntlProvider
    locale="en"
    messages={messages}
    defaultRichTextElements={{
      b: (chunk) => <strong>{chunk}</strong>,
    }}
  >
    {children}
  </IntlProvider>
);

const StyleProvider: React.FC = ({ children }) => (
  <ThemeProvider theme={theme}>
    <GlobalStyle />
    {children}
  </ThemeProvider>
);

const Services: React.FC = ({ children }) => (
  <AnalyticsProvider>
    <ApiErrorBoundary>
      <NotificationServiceProvider>
        <FeatureService>
          <AppServicesProvider>
            <AuthenticationProvider>
              <IntercomProvider>{children}</IntercomProvider>
            </AuthenticationProvider>
          </AppServicesProvider>
        </FeatureService>
      </NotificationServiceProvider>
    </ApiErrorBoundary>
  </AnalyticsProvider>
);

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <I18NProvider>
          <StoreProvider>
            <Suspense fallback={<LoadingPage />}>
              <ConfigProvider>
                <Router>
                  <Services>
                    <Routing />
                  </Services>
                </Router>
              </ConfigProvider>
            </Suspense>
          </StoreProvider>
        </I18NProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default React.memo(App);
