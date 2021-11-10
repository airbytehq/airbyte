import { Router } from "react-router-dom";
import * as React from "react";
import { IntlProvider } from "react-intl";
import { createMemoryHistory } from "history";
import { ThemeProvider } from "styled-components";

// TODO: theme was not working correctly so imported directly
import { theme, Theme } from "../src/theme";
import GlobalStyle from "../src/global-styles";
import messages from "../src/locales/en.json";
import { FeatureService } from "../src/hooks/services/Feature";
import { ConfigServiceProvider, defaultConfig } from "../src/config";

interface Props {
  theme?: Theme;
}

interface Props {
  children?: React.ReactNode;
  theme?: Theme;
}

class WithProviders extends React.Component<Props> {
  render() {
    const { children } = this.props;

    return (
      <Router history={createMemoryHistory()}>
        <FeatureService>
          <IntlProvider messages={messages} locale={"en"}>
            <ThemeProvider theme={theme}>
              <ConfigServiceProvider
                defaultConfig={defaultConfig}
                providers={[]}
              >
                <GlobalStyle />
                {children}
              </ConfigServiceProvider>
            </ThemeProvider>
          </IntlProvider>
        </FeatureService>
      </Router>
    );
  }
}

export default WithProviders;
