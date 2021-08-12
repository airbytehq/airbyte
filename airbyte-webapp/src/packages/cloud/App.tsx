import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";
import { QueryClient, QueryClientProvider } from "react-query";

import en from "locales/en.json";
import cloudLocales from "./locales/en.json";
import GlobalStyle from "global-styles";
import { theme } from "./theme";

import "packages/cloud/config/firebase";

import { Routing } from "./routes";
import LoadingPage from "components/LoadingPage";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import NotificationServiceProvider from "components/hooks/services/Notification";
import { AnalyticsInitializer } from "views/common/AnalyticsInitializer";
import {
  AuthenticationProvider,
  useAuthService,
} from "./services/auth/AuthService";
import { FeatureService } from "components/hooks/services/Feature";
import { registerService } from "core/servicesProvider";
import {
  useGetWorkspace,
  useWorkspaceService,
} from "./services/workspaces/WorkspacesService";

const queryClient = new QueryClient();

const messages = Object.assign({}, en, cloudLocales);

// TODO: move to proper place
const useCustomerIdProvider = () => {
  const { user } = useAuthService();
  return user?.userId ?? "";
};

registerService("currentWorkspaceProvider", () => {
  const { currentWorkspaceId } = useWorkspaceService();
  const { data: workspace } = useGetWorkspace(currentWorkspaceId ?? "");

  return workspace;
});

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <IntlProvider locale="en" messages={messages}>
          <QueryClientProvider client={queryClient}>
            <CacheProvider>
              <Suspense fallback={<LoadingPage />}>
                <FeatureService>
                  <ApiErrorBoundary>
                    <NotificationServiceProvider>
                      <AuthenticationProvider>
                        <AnalyticsInitializer
                          customerIdProvider={useCustomerIdProvider}
                        >
                          <Routing />
                        </AnalyticsInitializer>
                      </AuthenticationProvider>
                    </NotificationServiceProvider>
                  </ApiErrorBoundary>
                </FeatureService>
              </Suspense>
            </CacheProvider>
          </QueryClientProvider>
        </IntlProvider>
      </ThemeProvider>
    </React.StrictMode>
  );
};

export default App;
