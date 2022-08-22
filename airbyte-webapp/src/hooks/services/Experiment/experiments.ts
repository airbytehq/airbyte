/**
 * When adding a new feature flag in LaunchDarkly to consume in code you'll need to make
 * sure to update the typing here.
 */

export interface Experiments {
  "connector.orderOverwrite": Record<string, number>;
  "authPage.rightSideUrl": string | undefined;
  "authPage.hideSelfHostedCTA": boolean;
  "authPage.signup.hideName": boolean;
  "authPage.signup.hideCompanyName": boolean;
  "authPage.oauth.google": boolean;
  "authPage.oauth.github": boolean;
  "authPage.oauth.google.signUpPage": boolean;
  "authPage.oauth.github.signUpPage": boolean;
}
