import scss from "./scss/export.module.scss";

// Load all theme variables from our SCSS variables
export const theme = {
  primaryColor: scss.primaryColor,
  primaryColor25: scss.primaryColor25,
  primaryColor12: scss.primaryColor12,
  mediumPrimaryColor: scss.mediumPrimaryColor,
  mediumPrimaryColor20: scss.mediumPrimaryColor20,
  darkPrimaryColor: scss.darkPrimaryColor,
  darkPrimaryColor60: scss.darkPrimaryColor60,
  brightPrimaryColor: scss.brightPrimaryColor,
  lightPrimaryColor: scss.lightPrimaryColor,

  brightColor: scss.brightColor,

  dangerColor: scss.dangerColor,
  dangerColor25: scss.dangerColor25,
  warningColor: scss.warningColor,
  warningBackgroundColor: scss.warningBackgroundColor,
  lightDangerColor: scss.lightDangerColor,
  dangerTransparentColor: scss.dangerTransparentColor,
  successColor: scss.successColor,
  successColor20: scss.successColor20,
  backgroundColor: scss.backgroundColor,
  shadowColor: scss.shadowColor,
  cardShadowColor: scss.cardShadowColor,

  textColor: scss.textColor,
  lightTextColor: scss.lightTextColor,
  textColor90: scss.textColor90,
  darkBlue90: scss.darkBlue90,
  greyColor70: scss.greyColor70,
  greyColor60: scss.greyColor60,
  greyColor55: scss.greyColor55,
  greyColor40: scss.greyColor40,
  greyColor30: scss.greyColor30,
  greyColor20: scss.greyColor20,
  greyColor10: scss.greyColor10,
  greyColor0: scss.greyColor0,

  whiteColor: scss.whiteColor,
  blackColor: scss.blackColor,
  beigeColor: scss.beigeColor,
  darkBeigeColor: scss.darkBeigeColor,
  borderTableColor: scss.borderTableColor,
  lightTableColor: scss.lightTableColor,
  darkGreyColor: scss.darkGreyColor,
  redColor: scss.redColor,
  lightRedColor: scss.lightRedColor,
  redTransparentColor: scss.redTransparentColor,
  transparentColor: scss.transparentColor,

  regularFont: scss.regularFont,
  highlightFont: scss.highlightFont,
  codeFont: scss.codeFont,
  italicFont: scss.italicFont,
};

export const barChartColors = ["#E8E8ED", "#AFAFC1"];

export type Theme = typeof theme;
