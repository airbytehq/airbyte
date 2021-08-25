import * as Fullstory from "@fullstory/browser";
import { Options } from "@asayerio/tracker";

import { SegmentAnalytics } from "core/analytics/types";

import { UiConfig, uiConfig } from "./uiConfig";

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

type PaperCupsConfig = {
  accountId: string;
  baseUrl: string;
  enableStorytime: boolean;
};

type Config = {
  ui: UiConfig;
  segment: { token: string };
  papercups: PaperCupsConfig;
  openreplay: Options;
  fullstory: Fullstory.SnippetOptions;
  apiUrl: string;
  healthCheckInterval: number;
  isDemo: boolean;
  version?: string;
};

const Version = window.AIRBYTE_VERSION;

const openReplayConfig: Options = {
  projectID: window.OPENREPLAY !== "disabled" ? 6611843272536134 : -1,
  obscureTextEmails: false,
  obscureInputEmails: false,
  revID: Version,
};

const paperCupsConfig: PaperCupsConfig = {
  accountId: "74560291-451e-4ceb-a802-56706ece528b",
  baseUrl: "https://app.papercups.io",
  enableStorytime:
    !process.env.REACT_APP_PAPERCUPS_DISABLE_STORYTIME &&
    window.PAPERCUPS_STORYTIME !== "disabled",
};

const fullStoryConfig: Fullstory.SnippetOptions = {
  orgId: "13AXQ4",
  devMode: window.FULLSTORY === "disabled",
};

const config: Config = {
  ui: uiConfig,
  segment: {
    token:
      window.TRACKING_STRATEGY === "segment"
        ? process.env.REACT_APP_SEGMENT_TOKEN ||
          "6cxNSmQyGSKcATLdJ2pL6WsawkzEMDAN"
        : "",
  },
  papercups: paperCupsConfig,
  openreplay: openReplayConfig,
  fullstory: fullStoryConfig,
  version: Version,
  apiUrl:
    window.API_URL ||
    process.env.REACT_APP_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`,
  healthCheckInterval: 10000,
  isDemo: window.IS_DEMO === "true",
};

export default config;
