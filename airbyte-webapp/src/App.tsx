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
import NotificationService from "components/hooks/services/Notification";
import { AnalyticsInitializer } from "views/common/AnalyticsInitializer";
import {
  useCurrentWorkspace,
  usePickFirstWorkspace,
} from "components/hooks/services/useWorkspace";
import { Feature, FeatureService } from "components/hooks/services/Feature";
import { registerService } from "./core/servicesProvider";

registerService("currentWorkspaceProvider", usePickFirstWorkspace);

function useCustomerIdProvider() {
  const workspace = useCurrentWorkspace();

  return workspace.customerId;
}

const Features: Feature[] = [
  {
    id: "ALLOW_UPLOAD_CUSTOM_IMAGE",
  },
];

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <IntlProvider locale="en" messages={en}>
          <CacheProvider>
            <Suspense fallback={<LoadingPage />}>
              <FeatureService features={Features}>
                <ApiErrorBoundary>
                  <NotificationService>
                    <AnalyticsInitializer
                      customerIdProvider={useCustomerIdProvider}
                    >
                      <Routing />
                    </AnalyticsInitializer>
                  </NotificationService>
                </ApiErrorBoundary>
              </FeatureService>
            </Suspense>
          </CacheProvider>
        </IntlProvider>
      </ThemeProvider>
    </React.StrictMode>
  );
};

export default App;
