import { createGlobalStyle, ThemeProps } from "styled-components";

import { Theme } from "./theme";

const GlobalStyle = createGlobalStyle<ThemeProps<Theme>>`
  #__next,
  html,
  body,
  #root {
    height: 100%;
    width: 100%;
    padding: 0;
    margin: 0;
    font-weight: normal;
    -webkit-font-smoothing: antialiased;
    color: ${({ theme }) => theme.textColor};
    font-family: ${({ theme }) => theme.regularFont};
    background: ${({ theme }) => theme.backgroundColor};
    font-size: 14px;
  }
  
  button, input, textarea {
    font-family: ${({ theme }) => theme.regularFont};
  }
  
  * {
    box-sizing: border-box;
  }
`;

export default GlobalStyle;
