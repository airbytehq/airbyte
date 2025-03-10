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

// const redirects = yaml.load(
//   fs.readFileSync(path.join(__dirname, "redirects.yml"), "utf-8")
// );

/** @type {import('@docusaurus/types').Config} */
const config = {
  markdown: {
    mermaid: true,
  },
  themes: ["@docusaurus/theme-mermaid"],
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
      '@docusaurus/plugin-content-docs',
      {
        id: 'platform',
        path: '../docs/platform',
        routeBasePath: '/platform',
        sidebarPath: './sidebar-platform.js',
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
      '@docusaurus/plugin-content-docs',
      {
        id: 'release_notes',
        path: '../docs/release_notes',
        routeBasePath: '/release_notes',
        sidebarPath: './sidebar-release_notes.js',
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
      '@docusaurus/plugin-content-docs',
      {
        id: 'connectors',
        path: '../docs/integrations',
        routeBasePath: '/integrations',
        sidebarPath: './sidebar-connectors.js',
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
    // Client-side redirect plugin - turning off for now to replace with Vercel server-side redirects
    // [
    //   "@docusaurus/plugin-client-redirects",
    //   {
    //     fromExtensions: ["html", "htm"], // /myPage.html -> /myPage
    //     redirects: redirects,
    //   },
    // ],
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
      algolia: {
        appId: "OYKDBC51MU",
        apiKey: "15c487fd9f7722282efd8fcb76746fce", // Public API key: it is safe to commit it
        indexName: "airbyte",
      },
      announcementBar: {
        id: 'try_airbyte_cloud',
        content:
          '<a target="_blank" rel="noopener noreferrer" href="https://cloud.airbyte.io/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=NavBar">Try Airbyte Cloud</a>! Free for 14 days, no credit card needed.',
        backgroundColor: '#615eff',
        textColor: '#ffffff',
        isCloseable: true,
      },
      navbar: {
        title: "",
        logo: {
          alt: "Simple, secure and extensible data integration",
          src: "img/logo-dark.png",
          srcDark: "img/logo-light.png",
          height: 40,
        },
        items: [
          {
            type: 'docSidebar',
            position: 'left',
            docsPluginId: "platform",
            sidebarId: 'platform',
            label: 'Airbyte platform',
          },
          {
            type: 'docSidebar',
            position: 'left',
            docsPluginId: "connectors",
            sidebarId: 'connectors',
            label: 'Connector catalog',
          },
          {
            type: 'docSidebar',
            position: 'left',
            docsPluginId: "release_notes",
            sidebarId: 'releaseNotes',
            label: 'Release notes',
          },
          {
            type: 'dropdown',
            label: 'More resources',
            position: 'left',
            items: [
              {
                label: 'Airbyte website',
                href: 'https://airbyte.io/',
              },
              {
                label: 'Tutorials',
                href: "https://airbyte.com/tutorials",
              },
              {
                label: 'Blog',
                href: "https://airbyte.com/blog",
              },
              {
                href: "https://support.airbyte.com/",
                label: "Support",
              },
            ],
          },
          // --- Right side ---
          // Platform docs version selector
          {
            type: 'docsVersion',
            position: 'right',
            to: '/platform',
            docsPluginId: 'platform',
            label: 'Version',
            dropdownActiveClassDisabled: true, // do not style the dropdown as active when viewing platform docs
          },
          {
            href: "https://status.airbyte.com",
            label: "Cloud status",
            className: "cloudStatusLink",
            position: "right",
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
