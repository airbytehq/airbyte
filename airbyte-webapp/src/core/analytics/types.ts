export const enum Namespace {
  SOURCE = "Source",
  DESTINATION = "Destination",
  CONNECTION = "Connection",
  CONNECTOR = "Connector",
  ONBOARDING = "Onboarding",
  USER = "User",
  CREDITS = "Credits",
  CONNECTOR_BUILDER = "ConnectorBuilder",
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

  // Connector Builder Actions
  CONNECTOR_BUILDER_START = "ConnectorBuilderStart",
  API_URL_CREATE = "ApiUrlCreated",
  AUTHENTICATION_METHOD_SELECT = "AuthenticationMethodSelect",
  USER_INPUT_SELECTE = "UserInputSelect",
  USER_INPUT_CREATE = "UserInputCreate",
  USER_INPUT_EDITE = "UserInputEdit",
  USER_INPUT_DELETE = "UserInputDelete",
  STREAM_SELECTE = "StreamSelect",
  STREAM_CREATE = "StreamCreate",
  STREAM_COPY = "StreamCopy",
  STREAM_TEST = "StreamTest",
  STREAM_TEST_SUCCESS = "StreamTestSuccess",
  STREAM_TEST_FAILURE = "StreamTestFailure",
}

export type EventParams = Record<string, unknown>;
