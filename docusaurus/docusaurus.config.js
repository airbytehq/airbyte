// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const yaml = require("js-yaml");
const fs = require("node:fs");
const path = require("node:path");

const { themes } = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

const docsHeaderDecoration = require("./src/remark/docsHeaderDecoration");
const productInformation = require("./src/remark/productInformation");
const connectorList = require("./src/remark/connectorList");
const specDecoration = require("./src/remark/specDecoration");

const redirects = yaml.load(
  fs.readFileSync(path.join(__dirname, "redirects.yml"), "utf-8")
);

/** @type {import('@docusaurus/types').Config} */
const config = {
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],
  title: "Airbyte Documentation",
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
  ],

  plugins: [
    [
      "@docusaurus/plugin-client-redirects",
      {
        fromExtensions: ["html", "htm"], // /myPage.html -> /myPage
        redirects: redirects,
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

  clientModules: [
    require.resolve("./src/scripts/fontAwesomeIcons.js"),
    require.resolve("./src/scripts/cloudStatus.js"),
  ],

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/",
          sidebarCollapsible: true,
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
          path: "../docs",
          exclude: ["**/*.inapp.md"],
          beforeDefaultRemarkPlugins: [specDecoration, connectorList], // use before-default plugins so TOC rendering picks up inserted headings
          remarkPlugins: [docsHeaderDecoration, productInformation],
        },
        blog: false,
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
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
            href: "https://airbyte.io/",
            position: "left",
            label: "About Airbyte",
          },
          {
            href: "https://airbyte.com/tutorials",
            label: "Tutorials",
            position: "left",
          },
          {
            href: "https://support.airbyte.com/",
            label: "Support",
            position: "left",
          },
          // --- Right side ---
          {
            href: "https://status.airbyte.com",
            label: "Cloud Status",
            className: "cloudStatusLink",
            position: "right",
          },
          {
            href: "https://cloud.airbyte.io/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=NavBar",
            label: "Try Airbyte Cloud",
            position: "right",
            className: "header-button",
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
      },
    }),
};

module.exports = config;
