import * as Fullstory from "@fullstory/browser";
import { SegmentAnalytics } from "core/analytics/types";
import { Options } from "@asayerio/tracker";

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

const Version = window.AIRBYTE_VERSION;

const OpenReplayConfig: Options = {
  projectID: window.OPENREPLAY !== "disabled" ? 6611843272536134 : -1,
  obscureTextEmails: false,
  obscureInputEmails: false,
  revID: Version,
};

const PaperCupsConfig: {
  accountId: string;
  baseUrl: string;
  enableStorytime: boolean;
} = {
  accountId: "74560291-451e-4ceb-a802-56706ece528b",
  baseUrl: "https://app.papercups.io",
  enableStorytime:
    !process.env.REACT_APP_PAPERCUPS_DISABLE_STORYTIME &&
    window.PAPERCUPS_STORYTIME !== "disabled",
};

const FullStoryConfig: Fullstory.SnippetOptions = {
  orgId: "13AXQ4",
  devMode: window.FULLSTORY === "disabled",
};

type Config = {
  ui: {
    helpLink: string;
    gitLink: string;
    updateLink: string;
    slackLink: string;
    docsLink: string;
    configurationArchiveLink: string;
    namespaceLink: string;
    normalizationLink: string;
    tutorialLink: string;
    technicalSupport: string;
  };
  segment: { token: string };
  papercups: {
    accountId: string;
    baseUrl: string;
    enableStorytime: boolean;
  };
  openreplay: Options;
  fullstory: Fullstory.SnippetOptions;
  apiUrl: string;
  healthCheckInterval: number;
  isDemo: boolean;
  version?: string;
};

const BASE_DOCS_LINK = "https://docs.airbyte.io";

const config: Config = {
  ui: {
    technicalSupport: `${BASE_DOCS_LINK}/troubleshooting/on-deploying`,
    helpLink: "https://airbyte.io/community",
    gitLink: "https://github.com/airbytehq/airbyte",
    updateLink: `${BASE_DOCS_LINK}/upgrading-airbyte`,
    slackLink: "https://slack.airbyte.io",
    docsLink: BASE_DOCS_LINK,
    configurationArchiveLink: `${BASE_DOCS_LINK}/tutorials/upgrading-airbyte`,
    normalizationLink: `${BASE_DOCS_LINK}/understanding-airbyte/connections#airbyte-basic-normalization`,
    namespaceLink: `${BASE_DOCS_LINK}/understanding-airbyte/namespaces`,
    tutorialLink:
      "https://www.youtube.com/watch?v=Rcpt5SVsMpk&feature=emb_logo",
  },
  segment: {
    token:
      window.TRACKING_STRATEGY === "segment"
        ? process.env.REACT_APP_SEGMENT_TOKEN ||
          "6cxNSmQyGSKcATLdJ2pL6WsawkzEMDAN"
        : "",
  },
  papercups: PaperCupsConfig,
  openreplay: OpenReplayConfig,
  fullstory: FullStoryConfig,
  version: Version,
  apiUrl:
    window.API_URL ||
    process.env.REACT_APP_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`,
  healthCheckInterval: 10000,
  isDemo: window.IS_DEMO === "true",
};

export default config;
