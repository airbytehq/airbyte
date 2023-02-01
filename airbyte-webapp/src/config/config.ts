import { AirbyteWebappConfig } from "./types";

export const config: AirbyteWebappConfig = {
  segment: {
    token: window.SEGMENT_TOKEN ?? process.env.REACT_APP_SEGMENT_TOKEN,
    enabled: !window.TRACKING_STRATEGY || window.TRACKING_STRATEGY === "segment",
  },
  apiUrl: window.API_URL ?? process.env.REACT_APP_API_URL ?? `http://${window.location.hostname}:8001/api`,
  connectorBuilderApiUrl:
    window.CONNECTOR_BUILDER_API_URL ??
    process.env.REACT_APP_CONNECTOR_BUILDER_API_URL ??
    `http://${window.location.hostname}:8003`,
  version: window.AIRBYTE_VERSION ?? "dev",
  integrationUrl: process.env.REACT_APP_INTEGRATION_DOCS_URLS ?? "/docs",
  oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
  cloudApiUrl: window.CLOUD_API_URL ?? process.env.REACT_APP_CLOUD_API_URL,
  cloudPublicApiUrl: process.env.REACT_APP_CLOUD_PUBLIC_API_URL,
  firebase: {
    apiKey: window.FIREBASE_API_KEY ?? process.env.REACT_APP_FIREBASE_API_KEY,
    authDomain: window.FIREBASE_AUTH_DOMAIN ?? process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
    authEmulatorHost: window.FIREBASE_AUTH_EMULATOR_HOST ?? process.env.REACT_APP_FIREBASE_AUTH_EMULATOR_HOST,
  },
  intercom: {
    appId: process.env.REACT_APP_INTERCOM_APP_ID,
  },
  launchDarkly: window.LAUNCHDARKLY_KEY ?? process.env.REACT_APP_LAUNCHDARKLY_KEY,
  datadog: {
    applicationId: window.REACT_APP_DATADOG_APPLICATION_ID ?? process.env.REACT_APP_DATADOG_APPLICATION_ID,
    clientToken: window.REACT_APP_DATADOG_CLIENT_TOKEN ?? process.env.REACT_APP_DATADOG_CLIENT_TOKEN,
    site: window.REACT_APP_DATADOG_SITE ?? process.env.REACT_APP_DATADOG_SITE,
    service: window.REACT_APP_DATADOG_SERVICE ?? process.env.REACT_APP_DATADOG_SERVICE,
  },
  sentryDsn: window.REACT_APP_SENTRY_DSN ?? process.env.REACT_APP_SENTRY_DSN,
  webappTag: window.REACT_APP_WEBAPP_TAG ?? process.env.REACT_APP_WEBAPP_TAG ?? "dev",
};

export class MissingConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "MissingConfigError";
  }
}
