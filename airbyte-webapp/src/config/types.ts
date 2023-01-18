declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
    AIRBYTE_VERSION?: string;
    API_URL?: string;
    CONNECTOR_BUILDER_API_URL?: string;
    CLOUD?: string;
    REACT_APP_DATADOG_APPLICATION_ID: string;
    REACT_APP_DATADOG_CLIENT_TOKEN: string;
    REACT_APP_DATADOG_SITE: string;
    REACT_APP_DATADOG_SERVICE: string;
    REACT_APP_SENTRY_DSN?: string;
    REACT_APP_WEBAPP_TAG?: string;
    REACT_APP_INTERCOM_APP_ID?: string;
    REACT_APP_INTEGRATION_DOCS_URLS?: string;
    SEGMENT_TOKEN?: string;
    LAUNCHDARKLY_KEY?: string;
    analytics: SegmentAnalytics.AnalyticsJS;
  }
}

export interface Config {
  segment: { token: string; enabled: boolean };
  apiUrl: string;
  connectorBuilderApiUrl: string;
  oauthRedirectUrl: string;
  healthCheckInterval: number;
  version?: string;
  integrationUrl: string;
  launchDarkly?: string;
}

export type DeepPartial<T> = {
  [P in keyof T]+?: DeepPartial<T[P]>;
};

export type ProviderAsync<T> = () => Promise<T>;
export type Provider<T> = () => T;

export type ValueProvider<T> = Array<ProviderAsync<DeepPartial<T>>>;

export type ConfigProvider<T extends Config = Config> = ProviderAsync<DeepPartial<T>>;
