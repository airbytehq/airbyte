// This file should contain all hard-coded outbound links we use in the UI.
// Everything that is exported via `links` here will be validated in the CI for it's
// existence as well as periodically checked that they are still reachable.

const BASE_DOCS_LINK = "https://docs.airbyte.com";

export const links = {
  dbtCommandsReference: "https://docs.getdbt.com/reference/dbt-commands",
  technicalSupport: `${BASE_DOCS_LINK}/troubleshooting/on-deploying`,
  termsLink: "https://airbyte.com/terms",
  privacyLink: "https://airbyte.com/privacy-policy",
  helpLink: "https://airbyte.com/community",
  gitLink: `${BASE_DOCS_LINK}/quickstart/deploy-airbyte`,
  updateLink: `${BASE_DOCS_LINK}/operator-guides/upgrading-airbyte`,
  productReleaseStages: `${BASE_DOCS_LINK}/project-overview/product-release-stages`,
  slackLink: "https://slack.airbyte.com",
  supportTicketLink: "https://airbyte.com/contact-support",
  docsLink: BASE_DOCS_LINK,
  configurationArchiveLink: `${BASE_DOCS_LINK}/operator-guides/upgrading-airbyte/`,
  normalizationLink: `${BASE_DOCS_LINK}/understanding-airbyte/connections#airbyte-basic-normalization`,
  namespaceLink: `${BASE_DOCS_LINK}/understanding-airbyte/namespaces`,
  tutorialLink: "https://www.youtube.com/watch?v=Rcpt5SVsMpk&feature=emb_logo",
  statusLink: "https://status.airbyte.io/",
  tutorialsLink: "https://airbyte.com/tutorials",
  syncModeLink: `${BASE_DOCS_LINK}/understanding-airbyte/connections`,
  demoLink: "https://demo.airbyte.io",
  contactSales: "https://airbyte.com/talk-to-sales",
  webpageLink: "https://airbyte.com",
  webhookVideoGuideLink: "https://www.youtube.com/watch?v=NjYm8F-KiFc",
  webhookGuideLink: `${BASE_DOCS_LINK}/operator-guides/configuring-sync-notifications/`,
  cronReferenceLink: "http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html",
  cloudAllowlistIPsLink: `${BASE_DOCS_LINK}/cloud/getting-started-with-airbyte-cloud/#allowlist-ip-address`,
  dataResidencySurvey: "https://forms.gle/Dr7MPTdt9k3xTinL8",
} as const;

export type OutboundLinks = typeof links;
