/**
 * Action codes are used to log specific runtime events that we want to analyse in datadog.
 * This is useful for tracking when and how frequently certain code paths on the frontend are
 * encountered in production.
 */
export enum AppActionCodes {
  LD_LOAD_FAILURE = "LD_LOAD_FAILURE", // LaunchDarkly did not load in time and was ignored
}
