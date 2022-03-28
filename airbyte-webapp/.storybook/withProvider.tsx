import { MemoryRouter } from "react-router-dom";
import { IntlProvider } from "react-intl";
import { ThemeProvider } from "styled-components";

// TODO: theme was not working correctly so imported directly
import { theme } from "../src/theme";
import GlobalStyle from "../src/global-styles";
import messages from "../src/locales/en.json";
import { FeatureService } from "../src/hooks/services/Feature";
import { ConfigServiceProvider, defaultConfig } from "../src/config";
import { ServicesProvider } from "../src/core/servicesProvider";
import {
  analyticsServiceContext,
  AnalyticsServiceProviderValue,
} from "../src/hooks/services/Analytics";

const AnalyticsContextMock: AnalyticsServiceProviderValue = ({
  analyticsContext: {},
  setContext: () => {},
  addContextProps: () => {},
  removeContextProps: () => {},
  service: {},
} as unknown) as AnalyticsServiceProviderValue;

export const withProviders = (getStory) => (
  <analyticsServiceContext.Provider value={AnalyticsContextMock}>
    <ServicesProvider>
      <MemoryRouter>
        <IntlProvider messages={messages} locale={"en"}>
          <ThemeProvider theme={theme}>
            <ConfigServiceProvider defaultConfig={defaultConfig} providers={[]}>
              <FeatureService>
                <GlobalStyle />
                {getStory()}
              </FeatureService>
            </ConfigServiceProvider>
          </ThemeProvider>
        </IntlProvider>
      </MemoryRouter>
    </ServicesProvider>
  </analyticsServiceContext.Provider>
);
