// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion
import "dotenv/config.js";

const { themes } = require("prism-react-renderer");
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

const docsHeaderDecoration = require("./src/remark/docsHeaderDecoration");
const enterpriseDocsHeaderInformation = require("./src/remark/enterpriseDocsHeaderInformation");
const productInformation = require("./src/remark/productInformation");
const connectorList = require("./src/remark/connectorList");
const specDecoration = require("./src/remark/specDecoration");
const docMetaTags = require("./src/remark/docMetaTags");
const addButtonToTitle = require("./src/remark/addButtonToTitle");

/** @type {import('@docusaurus/types').Config} */
const config = {
  markdown: {
    mermaid: true,
  },
  themes: ["@docusaurus/theme-mermaid"],
  title: "Airbyte Docs",
  tagline:
    "Airbyte is an open-source data integration platform to build ELT pipelines. Consolidate your data in your data warehouses, lakes and databases.",
  url: "https://docs.airbyte.com/",
  // Assumed relative path.  If you are using airbytehq.github.io use /
  // anything else should match the repo name
  baseUrl: "/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "throw",
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
            addButtonToTitle,
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
    // This plugin controls "platform" docs, which are versioned
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "platform",
        path: "../docs/platform",
        routeBasePath: "/platform",
        sidebarPath: "./sidebar-platform.js",
        editUrl: ({ version, docPath }) => {
          if (version === "current") {
            // For the "next" (unreleased) version
            return `https://github.com/airbytehq/airbyte/edit/master/docs/platform/${docPath}`;
          } else {
            // For released versions
            return `https://github.com/airbytehq/airbyte/edit/master/docusaurus/platform_versioned_docs/version-${version}/${docPath}`;
          }
        },
        remarkPlugins: [
          docsHeaderDecoration,
          enterpriseDocsHeaderInformation,
          productInformation,
          docMetaTags,
          addButtonToTitle,
        ],
      },
    ],
    // This plugin controls Airbyte Embedded docs, which are not versioned
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "embedded",
        path: "../docs/embedded",
        routeBasePath: "/embedded",
        sidebarPath: "./sidebar-embedded.js",
        editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
        remarkPlugins: [
          docsHeaderDecoration,
          enterpriseDocsHeaderInformation,
          productInformation,
          docMetaTags,
          addButtonToTitle,
        ],
      },
    ],
    // This plugin controls release notes, which are not versioned
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
          addButtonToTitle,
        ],
      },
    ],
    // This plugin controls Connector docs, which are unversioned
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
    require.resolve("./src/plugins/enterpriseConnectors"),
    [
      "@signalwire/docusaurus-plugin-llms-txt",
      {
        siteTitle: "docs.airbyte.com llms.txt",
        siteDescription:
          "Airbyte is an open source platform designed for building and managing data pipelines, offering extensive connector options to facilitate data movement from various sources to destinations efficiently and effectively.",
        depth: 4,
        content: {
          includePages: true,
        },
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
    markpromptProjectKey:
      process.env.MARKPROMPT_PROJECT_KEY ||
      "sk_test_cbPFAzAxUvafRj6l1yjzrESu0bRpzQGK",
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
      algolia: {
        appId: "OYKDBC51MU",
        apiKey: "15c487fd9f7722282efd8fcb76746fce", // Public API key: it is safe to commit it
        indexName: "airbyte",
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
            type: "docSidebar",
            position: "left",
            docsPluginId: "embedded",
            sidebarId: "embedded",
            label: "Airbyte Embedded",
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
