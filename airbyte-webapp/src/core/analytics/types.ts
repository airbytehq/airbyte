export interface SegmentAnalytics {
  page: (name?: string) => void;
  reset: () => void;
  alias: (newId: string) => void;
  track: (name: string, properties: Record<string, unknown>) => void;
  identify: (userId?: string, traits?: Record<string, unknown>) => void;
  group: (organisationId: string, traits: Record<string, unknown>) => void;
}

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
  FEEDBACK = "Feedback",
  PREFERENCES = "Preferences",
  NO_MATCHING_CONNECTOR = "NoMatchingConnector",
  SELECTION_OPENED = "SelectionOpened",
  CHECKOUT_START = "CheckoutStart",
}

export type EventParams = Record<string, unknown>;
