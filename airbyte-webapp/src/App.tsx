import React, { Suspense } from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
import { CacheProvider } from "rest-hooks";

import en from "./locales/en.json";
import GlobalStyle from "./global-styles";
import { theme } from "./theme";

import { Routing } from "./pages/routes";
import LoadingPage from "./components/LoadingPage";
import NetworkErrorBoundary from "./components/NetworkErrorBoundary";

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <IntlProvider locale="en" messages={en}>
          <CacheProvider>
            <Suspense fallback={<LoadingPage />}>
              <NetworkErrorBoundary>
                <Routing />
              </NetworkErrorBoundary>
            </Suspense>
          </CacheProvider>
        </IntlProvider>
      </ThemeProvider>
    </React.StrictMode>
  );
};

export default App;
