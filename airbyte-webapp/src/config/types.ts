import { SegmentAnalytics } from "core/analytics/types";
import { UiConfig } from "./uiConfig";
import { Options as OpenReplayOptions } from "@asayerio/tracker";
import * as Fullstory from "@fullstory/browser";

declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
    PAPERCUPS_STORYTIME?: string;
    FULLSTORY?: string;
    OPENREPLAY?: string;
    AIRBYTE_VERSION?: string;
    API_URL?: string;
    IS_DEMO?: string;
    analytics: SegmentAnalytics;
  }
}

export type PaperCupsConfig = {
  accountId: string;
  baseUrl: string;
  enableStorytime: boolean;
};

export type Config = {
  ui: UiConfig;
  segment: { token: string; enabled: boolean };
  papercups: PaperCupsConfig;
  openreplay: OpenReplayOptions;
  fullstory: Fullstory.SnippetOptions;
  apiUrl: string;
  healthCheckInterval: number;
  isDemo: boolean;
  version?: string;
};

export type DeepPartial<T> = {
  [P in keyof T]+?: DeepPartial<T[P]>;
};

export type Provider<T> = () => Promise<T>;

export type ValueProvider<T> = [Provider<T>, ...Provider<DeepPartial<T>>[]];

export type ConfigProvider<T extends Config = Config> = Provider<
  DeepPartial<T>
>;
