import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";
import { BrowserRouter as Router } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";

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

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      suspense: true,
    },
  },
});

const StoreProvider: React.FC = ({ children }) => (
  <CacheProvider>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  </CacheProvider>
);

const Services: React.FC = ({ children }) => (
  <ConfigProvider>
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
  </ConfigProvider>
);

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <StyleProvider>
        <I18NProvider>
          <StoreProvider>
            <Suspense fallback={<LoadingPage />}>
              <Router>
                <Services>
                  <Routing />
                </Services>
              </Router>
            </Suspense>
          </StoreProvider>
        </I18NProvider>
      </StyleProvider>
    </React.StrictMode>
  );
};

export default React.memo(App);
