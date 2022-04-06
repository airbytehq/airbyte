const BASE_DOCS_LINK = "https://docs.airbyte.io";

const uiConfig = {
  technicalSupport: `${BASE_DOCS_LINK}/troubleshooting/on-deploying`,
  termsLink: "https://airbyte.com/terms",
  privacyLink: "https://airbyte.com/privacy-policy",
  helpLink: "https://airbyte.com/community",
  gitLink: "https://docs.airbyte.com/quickstart/deploy-airbyte",
  updateLink: `${BASE_DOCS_LINK}/upgrading-airbyte`,
  productReleaseStages: `${BASE_DOCS_LINK}/project-overview/product-release-stages`,
  slackLink: "https://slack.airbyte.com",
  supportTicketLink: "https://airbyte.com/contact-support",
  docsLink: BASE_DOCS_LINK,
  configurationArchiveLink: `${BASE_DOCS_LINK}/tutorials/upgrading-airbyte`,
  normalizationLink: `${BASE_DOCS_LINK}/understanding-airbyte/connections#airbyte-basic-normalization`,
  namespaceLink: `${BASE_DOCS_LINK}/understanding-airbyte/namespaces`,
  tutorialLink: "https://www.youtube.com/watch?v=Rcpt5SVsMpk&feature=emb_logo",
  statusLink: "https://status.airbyte.io/",
  recipesLink: "https://airbyte.com/recipes",
  syncModeLink: "https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history",
  demoLink: "https://demo.airbyte.io",
  contactSales: "https://airbyte.com/talk-to-sales",
  webpageLink: "https://airbyte.com",
} as const;

type UiConfig = Record<keyof typeof uiConfig, string>;

export type { UiConfig };
export { uiConfig };
