import { Router } from "react-router-dom";
import * as React from "react";
import { IntlProvider } from "react-intl";
import { createMemoryHistory } from "history";
import { ThemeProvider } from "styled-components";

// TODO: theme was not working correctly so imported directly
import { theme, Theme } from "../src/theme";
import GlobalStyle from "../src/global-styles";
import messages from "../src/locales/en.json";

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
        <IntlProvider messages={messages} locale={"en"}>
          <ThemeProvider theme={theme}>
            <GlobalStyle />
            {children}
          </ThemeProvider>
        </IntlProvider>
      </Router>
    );
  }
}

export default WithProviders;
