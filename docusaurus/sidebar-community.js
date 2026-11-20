const contributeToAirbyte = {
  type: "category",
  label: "Contribute to Airbyte",
  link: {
    type: "doc",
    id: "contributing-to-airbyte/README",
  },
  items: [
    "contributing-to-airbyte/issues-and-requests",
    "contributing-to-airbyte/developing-locally",
    "contributing-to-airbyte/writing-docs",
    "contributing-to-airbyte/resources/pull-requests-handbook",
    "contributing-to-airbyte/resources/qa-checks",
  ],
};

const licenses = {
  type: "category",
  label: "Licenses",
  link: {
    type: "doc",
    id: "licenses/README",
  },
  items: [
    "licenses/license-faq",
    "licenses/elv2-license",
    "licenses/mit-license",
    "licenses/examples",
  ],
};

const newsletterArchive = {
  type: "category",
  collapsible: true,
  collapsed: true,
  label: "Newsletter Archive",
  link: {
    type: "doc",
    id: "newsletter-archive/README",
  },
  items: [
    "newsletter-archive/aug-2026-semantic-search-now-covers-google-drive-and-granola",
    "newsletter-archive/jul-2026-agents-can-now-write-to-salesforce-and-hubspot",
    "newsletter-archive/jun-2026-airbyte-agents-now-supports-teams",
    "newsletter-archive/may-2026-three-ways-to-build-with-airbyte-agents",
    "newsletter-archive/feb-2026-context-store",
    "newsletter-archive/dec-2025-airbyte-agent-connectors",
    "newsletter-archive/oct-2025-introducing-airbyte-plus",
    "newsletter-archive/apr-2023-airbyte-hits-10k-github-stars",
    "newsletter-archive/jun-2022-our-progress-in-2022",
    "newsletter-archive/may-2022-updates-to-connector-release-stages",
    "newsletter-archive/apr-2022-airbyte-public-roadmap",
    "newsletter-archive/apr-2022-build-go-based-connectors",
    "newsletter-archive/mar-2022-airbytes-first-launch-week",
    "newsletter-archive/feb-2022-the-deck-we-used-to-raise-our-series-b",
    "newsletter-archive/jan-2022-airbyte-raises-a-150m-series-b",
    "newsletter-archive/dec-2021-connector-reliability-as-the-primary-focus",
    "newsletter-archive/nov-2021-how-to-commoditize-all-data-integration",
    "newsletter-archive/oct-2021-a-new-license-to-future-proof-the-commoditization-of-data-integration",
    "newsletter-archive/sep-2021-welcome-to-the-connector-marketplace",
    "newsletter-archive/aug-2021-write-for-the-community",
    "newsletter-archive/jul-2021-welcome-to-airbyte-recipes",
    "newsletter-archive/jun-2021-first-class-support-of-kubernetes",
    "newsletter-archive/jun-2021-how-we-raised-our-series-a-with-benchmark",
    "newsletter-archive/may-2021-our-series-a-round-with-benchmark",
    "newsletter-archive/may-2021-our-connector-development-kit",
    "newsletter-archive/apr-2021-official-airflow-provider",
    "newsletter-archive/feb-2021-our-seed-round-airflow-preview",
    "newsletter-archive/jan-2021-connectors-health-status-okrs-q1-21",
    "newsletter-archive/jan-2021-1st-version-of-the-airbyte-api",
    "newsletter-archive/dec-2020-release-of-incremental-append",
    "newsletter-archive/dec-2020-10-more-new-connectors",
    "newsletter-archive/nov-2020-9-new-connectors",
    "newsletter-archive/nov-2020-10-new-connectors",
    "newsletter-archive/oct-2020-start-building-your-own-connector",
    "newsletter-archive/oct-2020-what-we-learned-from-our-soft-launch",
  ],
};

module.exports = {
  community: [
    {
      type: "category",
      collapsible: false,
      label: "Community & support",
      link: {
        type: "doc",
        id: "README",
      },
      items: [
        "getting-support",
        contributeToAirbyte,
        "code-of-conduct",
        licenses,
        newsletterArchive,
      ],
    },
  ],
};
