import { SegmentAnalytics } from "core/analytics/types";

import { OutboundLinks } from "./links";

declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
    AIRBYTE_VERSION?: string;
    API_URL?: string;
    CLOUD?: string;
    REACT_APP_SENTRY_DSN?: string;
    REACT_APP_WEBAPP_TAG?: string;
    REACT_APP_INTERCOM_APP_ID?: string;
    REACT_APP_INTEGRATION_DOCS_URLS?: string;
    SEGMENT_TOKEN?: string;
    LAUNCHDARKLY_KEY?: string;
    analytics: SegmentAnalytics;
  }
}

export interface Config {
  links: OutboundLinks;
  segment: { token: string; enabled: boolean };
  apiUrl: string;
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
