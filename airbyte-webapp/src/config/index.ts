import { SegmentAnalytics } from "core/analytics/types";

declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
    PAPERCUPS_STORYTIME?: string;
    FULLSTORY?: string;
    AIRBYTE_VERSION?: string;
    API_URL?: string;
    IS_DEMO?: string;
    analytics: SegmentAnalytics;
  }
}

type Config = {
  ui: {
    helpLink: string;
    slackLink: string;
    docsLink: string;
    configurationArchiveLink: string;
    namespaceLink: string;
    normalizationLink: string;
    workspaceId: string;
    tutorialLink: string;
    technicalSupport: string;
  };
  segment: { token: string };
  papercups: {
    accountId: string;
    baseUrl: string;
    enableStorytime: boolean;
  };
  fullstory: {
    org: string;
  };
  apiUrl: string;
  healthCheckInterval: number;
  isDemo: boolean;
  version?: string;
};

const config: Config = {
  ui: {
    technicalSupport: "https://docs.airbyte.io/troubleshooting/on-deploying",
    helpLink: "https://airbyte.io/community",
    slackLink: "https://slack.airbyte.io",
    docsLink: "https://docs.airbyte.io",
    configurationArchiveLink:
      "https://docs.airbyte.io/tutorials/upgrading-airbyte",
    normalizationLink:
      "https://docs.airbyte.io/understanding-airbyte/namespaces.md",
    namespaceLink:
      "https://docs.airbyte.io/understanding-airbyte/connections#airbyte-basic-normalization",
    tutorialLink:
      "https://www.youtube.com/watch?v=Rcpt5SVsMpk&feature=emb_logo",
    workspaceId: "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6",
  },
  segment: {
    token:
      window.TRACKING_STRATEGY === "segment"
        ? process.env.REACT_APP_SEGMENT_TOKEN ||
          "6cxNSmQyGSKcATLdJ2pL6WsawkzEMDAN"
        : "",
  },
  papercups: {
    accountId: "74560291-451e-4ceb-a802-56706ece528b",
    baseUrl: "https://app.papercups.io",
    enableStorytime: window.PAPERCUPS_STORYTIME !== "disabled",
  },
  fullstory: {
    org: window.FULLSTORY === "disabled" ? "" : "13AXQ4",
  },
  version: window.AIRBYTE_VERSION,
  apiUrl:
    window.API_URL ||
    process.env.REACT_APP_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`,
  healthCheckInterval: 10000,
  isDemo: window.IS_DEMO === "true",
};

export default config;
