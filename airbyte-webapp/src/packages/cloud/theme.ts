import { theme as rootTheme } from "theme";

export const theme = {
  ...rootTheme,

  primaryColor: "#615EFF",
  textColor: "#1A194D",
  backgroundColor: "#FEF9F4",

  h1: {
    fontSize: "24px",
    lineHeight: "29px",
  },
  h2: {
    fontSize: "22px",
    lineHeight: "27px",
  },
  h3: {
    fontSize: "20px",
    lineHeight: "25px",
  },
  h4: {
    fontSize: "18px",
    lineHeight: "22px",
  },
  h5: {
    fontSize: "16px",
    lineHeight: "28px",
  },
};

export type Theme = typeof theme;
