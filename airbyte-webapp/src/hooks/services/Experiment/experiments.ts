/* eslint sort-keys: "error" */
/**
 * Experiments are short-term flags for A/B testing or staged rollouts of features.
 *
 * When adding a new feature flag in LaunchDarkly to consume in code you'll need to make
 * sure to update the typing here.
 */

export interface Experiments {
  "connector.inviteUsersHint.visible": boolean;
  "connector.inviteUsersHint.linkToUsersPage": boolean;
  "connector.orderOverwrite": Record<string, number>;
  "connector.frequentlyUsedDestinationIds": string[];
  "connector.form.useDatepicker": boolean;
  "connector.shortSetupGuides": boolean;
  "authPage.rightSideUrl": string | undefined;
  "authPage.hideSelfHostedCTA": boolean;
  "authPage.signup.hideName": boolean;
  "authPage.signup.hideCompanyName": boolean;
  "authPage.oauth.google": boolean;
  "authPage.oauth.github": boolean;
  "authPage.oauth.google.signUpPage": boolean;
  "authPage.oauth.github.signUpPage": boolean;
  "onboarding.speedyConnection": boolean;
  "authPage.oauth.position": "top" | "bottom";
  "connection.onboarding.sources": string;
  "connection.onboarding.destinations": string;
  "connection.autoDetectSchemaChanges": boolean;
  "connection.columnSelection": boolean;
  "connection.newTableDesign": boolean;
  "workspace.freeConnectorsProgram.visible": boolean;
}
