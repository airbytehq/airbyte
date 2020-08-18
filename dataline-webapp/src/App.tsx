import React from "react";
import { ThemeProvider } from "styled-components";
import { IntlProvider } from "react-intl";
// import { CacheProvider } from "rest-hooks";
import { hot } from "react-hot-loader/root";

import en from "./locales/en.json";
import GlobalStyle from "./global-styles";
import { theme } from "./theme";

import { Routing } from "./pages/routes";

const App = () => {
  return (
    <>
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <IntlProvider locale={"en"} messages={en}>
          <Routing />
        </IntlProvider>
      </ThemeProvider>
    </>
  );
};

export default process.env.NODE_ENV === "development" ? hot(App) : App;
