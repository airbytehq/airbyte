import { MemoryRouter } from "react-router-dom";
import * as React from "react";
import { IntlProvider } from "react-intl";
import { ThemeProvider } from "styled-components";

// TODO: theme was not working correctly so imported directly
import { theme } from "../src/theme";
import GlobalStyle from "../src/global-styles";
import messages from "../src/locales/en.json";
import { FeatureService } from "../src/hooks/services/Feature";
import { ConfigServiceProvider, defaultConfig } from "../src/config";
import { ServicesProvider } from "../src/core/servicesProvider";

export const withProviders = (getStory) => (
  <ServicesProvider>
    <MemoryRouter>
      <IntlProvider messages={messages} locale={"en"}>
        <ThemeProvider theme={theme}>
          <ConfigServiceProvider
            defaultConfig={defaultConfig}
            providers={[]}
          >
            <FeatureService>
              <GlobalStyle />
              {getStory()}
            </FeatureService>
          </ConfigServiceProvider>
        </ThemeProvider>
      </IntlProvider>
    </MemoryRouter>
  </ServicesProvider>
);
