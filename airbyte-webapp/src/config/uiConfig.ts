const BASE_DOCS_LINK = "https://docs.airbyte.io";

type UiConfig = {
  helpLink: string;
  gitLink: string;
  updateLink: string;
  slackLink: string;
  termsLink: string;
  privacyLink: string;
  docsLink: string;
  configurationArchiveLink: string;
  namespaceLink: string;
  normalizationLink: string;
  tutorialLink: string;
  technicalSupport: string;
};

const uiConfig: UiConfig = {
  technicalSupport: `${BASE_DOCS_LINK}/troubleshooting/on-deploying`,
  termsLink: "https://airbyte.io/terms",
  privacyLink: "https://airbyte.io/privacy-policy",
  helpLink: "https://airbyte.io/community",
  gitLink: "https://github.com/airbytehq/airbyte",
  updateLink: `${BASE_DOCS_LINK}/upgrading-airbyte`,
  slackLink: "https://slack.airbyte.io",
  docsLink: BASE_DOCS_LINK,
  configurationArchiveLink: `${BASE_DOCS_LINK}/tutorials/upgrading-airbyte`,
  normalizationLink: `${BASE_DOCS_LINK}/understanding-airbyte/connections#airbyte-basic-normalization`,
  namespaceLink: `${BASE_DOCS_LINK}/understanding-airbyte/namespaces`,
  tutorialLink: "https://www.youtube.com/watch?v=Rcpt5SVsMpk&feature=emb_logo",
};

export type { UiConfig };
export { uiConfig };
