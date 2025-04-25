// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion
import "dotenv/config.js";
const yaml = require("js-yaml");
const fs = require("node:fs");
const path = require("node:path");

const { themes } = require("prism-react-renderer");
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

const docsHeaderDecoration = require("./src/remark/docsHeaderDecoration");
const enterpriseDocsHeaderInformation = require("./src/remark/enterpriseDocsHeaderInformation");
const productInformation = require("./src/remark/productInformation");
const connectorList = require("./src/remark/connectorList");
const specDecoration = require("./src/remark/specDecoration");
const docMetaTags = require("./src/remark/docMetaTags");

/** @type {import('@docusaurus/types').Config} */
const config = {
  markdown: {
    mermaid: true,
  },
  themes: ["@docusaurus/theme-mermaid", "@markprompt/docusaurus-theme-search"],
  title: "Airbyte Documentation",
  tagline:
    "Airbyte is an open-source data integration platform to build ELT pipelines. Consolidate your data in your data warehouses, lakes and databases.",
  url: "https://docs.airbyte.com/",
  // Assumed relative path.  If you are using airbytehq.github.io use /
  // anything else should match the repo name
  baseUrl: "/",
  onBrokenLinks: "warn",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.png",
  organizationName: "airbytehq", // Usually your GitHub org/user name.
  projectName: "airbyte", // Usually your repo name.

  // Adds one off script tags to the head of each page
  // e.g. <script async data-api-key="..." id="unifytag" src="..."></script>
  scripts: [
    {
      src: "https://cdn.unifygtm.com/tag/v1/unify-tag-script.js",
      async: true,
      type: "module",
      id: "unifytag",
      "data-api-key": "wk_BEtrdAz2_2qgdexg5KRa6YWLWVwDdieFC7CAHkDKz",
    },
    {
      src: "https://cdn.jsdelivr.net/npm/hockeystack@latest/hockeystack.min.js",
      async: true,
      "data-apikey": "2094e2379643f69f7aec647a15f786",
      "data-cookieless": "1",
      "data-auto-identify": "1",
    },
  ],
  headTags: [
    {
      tagName: "meta",
      attributes: {
        name: "zd-site-verification",
        content: "plvcr4wcl9abmq0itvi63c",
      },
    },
    {
      tagName: "meta",
      attributes: {
        name: "google-site-verification",
        content: "3bGvGd17EJ-wHoyGlRszHtmMGmtWGQ4dDFEQy8ampQ0",
      },
    },
  ],
  // The preset is the "main" docs instance, though in reality, most content does not live under this preset. See the plugins array below, which defines the behavior of each docs instance.
  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/",
          sidebarCollapsible: true,
          sidebarPath: require.resolve("./sidebar.js"),
          editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
          path: "../docs/home",
          beforeDefaultRemarkPlugins: [specDecoration, connectorList], // use before-default plugins so TOC rendering picks up inserted headings
          remarkPlugins: [
            docsHeaderDecoration,
            enterpriseDocsHeaderInformation,
            productInformation,
            docMetaTags,
          ],
        },
        blog: false,
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],
  plugins: [
    // This plugin controls "platform" docs, which are to be versioned
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "platform",
        path: "../docs/platform",
        routeBasePath: "/platform",
        sidebarPath: "./sidebar-platform.js",
        editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
        remarkPlugins: [
          docsHeaderDecoration,
          enterpriseDocsHeaderInformation,
          productInformation,
          docMetaTags,
        ],
      },
    ],
    // This plugin controls release notes, which are unversioned
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "release_notes",
        path: "../docs/release_notes",
        routeBasePath: "/release_notes",
        sidebarPath: "./sidebar-release_notes.js",
        editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
        remarkPlugins: [
          docsHeaderDecoration,
          enterpriseDocsHeaderInformation,
          productInformation,
          docMetaTags,
        ],
      },
    ],
    // This plugin controls "connector/source/destination" docs, which are unversioned by Docusaurus and use their own versioning
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "connectors",
        path: "../docs/integrations",
        routeBasePath: "/integrations",
        sidebarPath: "./sidebar-connectors.js",
        editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
        beforeDefaultRemarkPlugins: [specDecoration, connectorList], // use before-default plugins so TOC rendering picks up inserted headings
        remarkPlugins: [
          docsHeaderDecoration,
          enterpriseDocsHeaderInformation,
          productInformation,
          docMetaTags,
        ],
      },
    ],
    () => ({
      name: "Yaml loader",
      configureWebpack() {
        return {
          module: {
            rules: [
              {
                test: /\.ya?ml$/,
                use: "yaml-loader",
              },
              {
                test: /\.html$/i,
                loader: "html-loader",
              },
            ],
          },
        };
      },
    }),
  ],
  customFields: {
    requestErdApiUrl: process.env.REQUEST_ERD_API_URL,
  },
  clientModules: [
    require.resolve("./src/scripts/cloudStatus.js"),
    require.resolve("./src/scripts/download-abctl-buttons.js"),
    require.resolve("./src/scripts/fontAwesomeIcons.js"),
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        disableSwitch: false,
      },
      docs: {
        sidebar: {
          autoCollapseCategories: true,
        },
      },
      markprompt: { // Our AI chat bot
        projectKey: "pk_c87ydSnE4o1tX9txQReh3vDvVnKDnbje", // Public project key. Safe to commit.
        chat: {
          assistantId: "d1399022-d7e2-4404-bd16-8b3ad2b5465b",
          enabled: true,
          defaultView: {
            message: "Hi! I'm Octavia. How can I help? **I'm an AI, but I'm still learning and might make mistakes**. ",
            prompts: [
              "What's Airbyte?",
              "Can I try Airbyte quickly?",
              "How do I use Terraform with Airbyte?",
              "Is there an enterprise version?"
            ]
          },
          avatars: {
            assistant: '/img/octavia-talking.png',
          }
        },
        // By setting `floating` to false, use the standard navbar search component.
        trigger: { floating: false },
        search: {
          enabled: true,
          provider: {
            name: "algolia",
            apiKey: "15c487fd9f7722282efd8fcb76746fce", // Public API key. Safe to commit.
            appId: "OYKDBC51MU",
            indexName: "airbyte",
          },
        },
      },
      announcementBar: {
        id: "try_airbyte_cloud",
        content:
          '<a target="_blank" rel="noopener noreferrer" href="https://cloud.airbyte.io/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=NavBar">Try Airbyte Cloud</a>! Free for 14 days, no credit card needed.',
        backgroundColor: "#615eff",
        textColor: "#ffffff",
        isCloseable: true,
      },
      navbar: {
        title: "Docs",
        logo: {
          alt: "Simple, secure and extensible data integration",
          src: "img/logo-dark.png",
          srcDark: "img/logo-light.png",
          height: 40,
        },
        items: [
          {
            type: "docSidebar",
            position: "left",
            docsPluginId: "platform",
            sidebarId: "platform",
            label: "Platform",
          },
          {
            type: "docSidebar",
            position: "left",
            docsPluginId: "connectors",
            sidebarId: "connectors",
            label: "Connectors",
          },
          {
            type: "docSidebar",
            position: "left",
            docsPluginId: "release_notes",
            sidebarId: "releaseNotes",
            label: "Release notes",
          },
          {
            href: "https://support.airbyte.com/",
            label: "Support",
          },

          {
            href: "https://status.airbyte.com",
            label: "Status",
            className: "cloudStatusLink",
          },
          // --- Right side ---
          // Platform docs version selector
          {
            type: "docsVersionDropdown",
            position: "right",
            docsPluginId: "platform",
            label: "Version",
            dropdownActiveClassDisabled: true, // do not style the dropdown as active when viewing platform docs
          },
          {
            href: "https://github.com/airbytehq",
            position: "right",
            "aria-label": "Airbyte on GitHub",
            className: "header-github-link",
          },
        ],
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ["bash", "diff", "json", "hcl"],
      },
    }),
};

module.exports = config;
