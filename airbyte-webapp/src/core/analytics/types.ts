export const enum Namespace {
  SOURCE = "Source",
  DESTINATION = "Destination",
  CONNECTION = "Connection",
  CONNECTOR = "Connector",
  ONBOARDING = "Onboarding",
  USER = "User",
  CREDITS = "Credits",
}

export const enum Action {
  CREATE = "Create",
  TEST = "Test",
  SELECT = "Select",
  SUCCESS = "TestSuccess",
  FAILURE = "TestFailure",
  FREQUENCY = "FrequencySet",
  SYNC = "FullRefreshSync",
  EDIT_SCHEMA = "EditSchema",
  DISABLE = "Disable",
  REENABLE = "Reenable",
  DELETE = "Delete",
  REQUEST = "Request",
  SKIP = "Skip",
  PREFERENCES = "Preferences",
  NO_MATCHING_CONNECTOR = "NoMatchingConnector",
  SELECTION_OPENED = "SelectionOpened",
  CHECKOUT_START = "CheckoutStart",
  LOAD_MORE_JOBS = "LoadMoreJobs",
  INVITE = "Invite",
}

export type EventParams = Record<string, unknown>;
