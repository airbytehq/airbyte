declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
  }
}

const config: {
  ui: {
    helpLink: string;
    docsLink: string;
    workspaceId: string;
    tutorialLink: string;
  };
  segment: { token: string };
  apiUrl: string;
} = {
  ui: {
    helpLink: "https://airbyte.io/community",
    docsLink: "https://docs.airbyte.io",
    tutorialLink:
      "https://www.youtube.com/watch?v=Rcpt5SVsMpk&feature=emb_logo",
    workspaceId: "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6"
  },
  segment: {
    token:
      window.TRACKING_STRATEGY === "segment"
        ? process.env.REACT_APP_SEGMENT_TOKEN ||
          "6cxNSmQyGSKcATLdJ2pL6WsawkzEMDAN"
        : ""
  },
  apiUrl:
    process.env.REACT_APP_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`
};

export default config;
