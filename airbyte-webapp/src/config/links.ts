// This file should contain all hard-coded outbound links we use in the UI.
// Everything that is exported via `links` here will be validated in the CI for it's
// existence as well as periodically checked that they are still reachable.

const BASE_DOCS_LINK = "https://docs.daspire.com";

export const links = {
  dbtCommandsReference: "https://docs.getdbt.com/reference/dbt-commands",
  technicalSupport: `${BASE_DOCS_LINK}/troubleshooting/on-deploying`,
  termsLink: "https://daspire.com/terms",
  privacyLink: "https://daspire.com/privacy-policy",
  helpLink: "https://daspire.com/community",
  gitLink: `${BASE_DOCS_LINK}/quickstart/deploy-airbyte`,
  updateLink: `${BASE_DOCS_LINK}/operator-guides/upgrading-airbyte`,
  productReleaseStages: `${BASE_DOCS_LINK}/project-overview/product-release-stages`,
  slackLink: "https://slack.daspire.com",
  supportTicketLink: "https://daspire.com/contact-support",
  docsLink: BASE_DOCS_LINK,
  configurationArchiveLink: `${BASE_DOCS_LINK}/operator-guides/upgrading-airbyte/`,
  normalizationLink: `${BASE_DOCS_LINK}/understanding-airbyte/connections#airbyte-basic-normalization`,
  namespaceLink: `${BASE_DOCS_LINK}/understanding-airbyte/namespaces`,
  tutorialLink: "https://www.youtube.com/watch?v=Rcpt5SVsMpk&feature=emb_logo",
  statusLink: "https://status.airbyte.io/",
  recipesLink: "https://daspire.com/recipes",
  syncModeLink: `${BASE_DOCS_LINK}/understanding-airbyte/connections`,
  demoLink: "https://demo.airbyte.io",
  contactSales: "https://daspire.com/talk-to-sales",
  webpageLink: "https://daspire.com",
} as const;

export type OutboundLinks = typeof links;
