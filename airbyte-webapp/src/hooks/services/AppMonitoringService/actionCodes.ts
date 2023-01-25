/**
 * Action codes are used to log specific runtime events that we want to analyse in datadog.
 * This is useful for tracking when and how frequently certain code paths on the frontend are
 * encountered in production.
 */
export enum AppActionCodes {
  /**
   * LaunchDarkly did not load in time and was ignored
   */
  LD_LOAD_TIMEOUT = "LD_LOAD_TIMEOUT",
}
