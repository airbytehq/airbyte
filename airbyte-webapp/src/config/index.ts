const config: {
  ui: { helpLink: string; docsLink: string; workspaceId: string };
  apiUrl: string;
} = {
  ui: {
    helpLink: "https://airbyte.io/community",
    docsLink: "https://docs.airbyte.io",
    workspaceId: "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6"
  },
  apiUrl:
    process.env.REACT_APP_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`
};

export default config;
