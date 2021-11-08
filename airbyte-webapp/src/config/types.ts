import { SegmentAnalytics } from "core/analytics/types";
import { UiConfig } from "./uiConfig";

declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
    AIRBYTE_VERSION?: string;
    API_URL?: string;
    IS_DEMO?: string;
    CLOUD?: string;
    REACT_APP_SENTRY_DSN?: string;
    REACT_APP_WEBAPP_TAG?: string;
    REACT_APP_INTERCOM_APP_ID?: string;
    REACT_APP_INTEGRATION_DOCS_URLS?: string;
    analytics: SegmentAnalytics;

    // API_URL to hack rest-hooks resources
    _API_URL: string;
  }
}

export type Config = {
  ui: UiConfig;
  segment: { token: string; enabled: boolean };
  apiUrl: string;
  oauthRedirectUrl: string;
  healthCheckInterval: number;
  isDemo: boolean;
  version?: string;
  integrationUrl: string;
};

export type DeepPartial<T> = {
  [P in keyof T]+?: DeepPartial<T[P]>;
};

export type ProviderAsync<T> = () => Promise<T>;
export type Provider<T> = () => T;

export type ValueProvider<T> = ProviderAsync<DeepPartial<T>>[];

export type ConfigProvider<T extends Config = Config> = ProviderAsync<
  DeepPartial<T>
>;
