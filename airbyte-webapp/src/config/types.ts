import * as Fullstory from "@fullstory/browser";

import { SegmentAnalytics } from "core/analytics/types";
import { UiConfig } from "./uiConfig";

declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
    FULLSTORY?: string;
    AIRBYTE_VERSION?: string;
    API_URL?: string;
    IS_DEMO?: string;
    CLOUD?: string;
    FIREBASE_API_KEY?: string;
    FIREBASE_AUTH_DOMAIN?: string;
    CLOUD_API_URL?: string;
    REACT_APP_SENTRY_DSN?: string;
    REACT_APP_WEBAPP_TAG?: string;
    REACT_APP_INTERCOM_APP_ID?: string;

    analytics: SegmentAnalytics;
    _API_URL: string;
  }
}

export type Config = {
  ui: UiConfig;
  segment: { token: string; enabled: boolean };
  fullstory: Fullstory.SnippetOptions;
  apiUrl: string;
  oauthRedirectUrl: string;
  healthCheckInterval: number;
  isDemo: boolean;
  version?: string;
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
