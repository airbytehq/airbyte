import "dotenv/config.js";
import type { Config } from "@docusaurus/types";
import { themes as prismThemes } from "prism-react-renderer";
import type { Options as ClassicPresetOptions } from "@docusaurus/preset-classic";
import fs from "fs";
import { PluginOptions as LLmPluginOptions } from "@signalwire/docusaurus-plugin-llms-txt";

// Import remark plugins
const docsHeaderDecoration = require("./src/remark/docsHeaderDecoration");
const enterpriseDocsHeaderInformation = require("./src/remark/enterpriseDocsHeaderInformation");
const productInformation = require("./src/remark/productInformation");
const connectorList = require("./src/remark/connectorList");
const specDecoration = require("./src/remark/specDecoration");
const docMetaTags = require("./src/remark/docMetaTags");
const addButtonToTitle = require("./src/remark/addButtonToTitle");
const npm2yarn = require("@docusaurus/remark-plugin-npm2yarn");

// Import constants
const {
  SPEC_CACHE_PATH,
  API_SIDEBAR_PATH,
} = require("./src/scripts/embedded-api/constants");

const lightCodeTheme = prismThemes.github;
const darkCodeTheme = prismThemes.dracula;

const config: Config = {
  future: {
    experimental_faster: {
      rspackBundler: true,
      rspackPersistentCache: true,
      swcJsMinimizer: true,
      swcJsLoader: true,
    },
  },
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: "throw",
    },
  },
  themes: [
    "@docusaurus/theme-mermaid",
    "@saucelabs/theme-github-codeblock",
    "docusaurus-theme-openapi-docs",
  ],
  title: "Airbyte Docs",
  tagline:
    "Airbyte is an open-source data integration platform to build ELT pipelines. Consolidate your data in your data warehouses, lakes and databases.",
  url: "https://docs.airbyte.com/",
  // Assumed relative path.  If you are using airbytehq.github.io use /
  // anything else should match the repo name
  baseUrl: "/",
  onBrokenLinks: "throw",

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
    ...(process.env.NODE_ENV === "production" && process.env.SEGMENT_WRITE_KEY
      ? [
          {
            tagName: "script",
            attributes: {
              name: "segment-script",
            },
            innerHTML: `
        !function(){var i="analytics",analytics=window[i]=window[i]||[];if(!analytics.initialize)if(analytics.invoked)window.console&&console.error&&console.error("Segment snippet included twice.");else{analytics.invoked=!0;analytics.methods=["trackSubmit","trackClick","trackLink","trackForm","pageview","identify","reset","group","track","ready","alias","debug","page","screen","once","off","on","addSourceMiddleware","addIntegrationMiddleware","setAnonymousId","addDestinationMiddleware","register"];analytics.factory=function(e){return function(){if(window[i].initialized)return window[i][e].apply(window[i],arguments);var n=Array.prototype.slice.call(arguments);if(["track","screen","alias","group","page","identify"].indexOf(e)>-1){var c=document.querySelector("link[rel='canonical']");n.push({__t:"bpc",c:c&&c.getAttribute("href")||void 0,p:location.pathname,u:location.href,s:location.search,t:document.title,r:document.referrer})}n.unshift(e);analytics.push(n);return analytics}};for(var n=0;n<analytics.methods.length;n++){var key=analytics.methods[n];analytics[key]=analytics.factory(key)}analytics.load=function(key,n){var t=document.createElement("script");t.type="text/javascript";t.async=!0;t.setAttribute("data-global-segment-analytics-key",i);t.src="https://cdn.segment.com/analytics.js/v1/" + key + "/analytics.min.js";var r=document.getElementsByTagName("script")[0];r.parentNode.insertBefore(t,r);analytics._loadOptions=n};analytics._writeKey="${process.env.SEGMENT_WRITE_KEY}";;analytics.SNIPPET_VERSION="5.2.0";
        analytics.load("${process.env.SEGMENT_WRITE_KEY}");
        analytics.page();
      }}();`,
          },
        ]
      : []),
  ],
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },
  // The preset is the "main" docs instance, though in reality, most content does not live under this preset. See the plugins array below, which defines the behavior of each docs instance.
  presets: [
    [
      "classic",
      {
        docs: false, // Disable default docs plugin since we're using a custom page for home
        blog: false,
        pages: {}, // Enable pages plugin for standalone pages
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      } satisfies ClassicPresetOptions,
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
    // This plugin controls AI Agent Tools docs, which are not versioned
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "ai-agents",
        path: "../docs/ai-agents",
        routeBasePath: "/ai-agents",
        sidebarPath: "./sidebar-ai-agents.js",
        editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
        remarkPlugins: [
          docsHeaderDecoration,
          enterpriseDocsHeaderInformation,
          productInformation,
          docMetaTags,
          addButtonToTitle,
          [npm2yarn, { sync: true }],
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
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "embedded-api",
        path: "api-docs/embedded-api",
        routeBasePath: "/embedded-api/",
        docItemComponent: "@theme/ApiItem",
        async sidebarItemsGenerator() {
          // We only want to include visible endpoints on the sidebar. We need to filter out endpoints with tags
          // that are not included in the spec. Even if we didn't need to filter out elements the OpenAPI plugin generates a sidebar.ts
          // file that exports a nested object, but Docusaurus expects just the array of sidebar items, so we need to extracts the actual sidebar
          // items from the generated file structure.

          try {
            const specPath = SPEC_CACHE_PATH;

            if (!fs.existsSync(specPath)) {
              console.warn(
                "Embedded API spec file not found, using empty sidebar",
              );
              return [];
            }

            const data = JSON.parse(fs.readFileSync(specPath, "utf8"));
            console.log("Loaded embedded API spec from cache");

            // Load the freshly generated sidebar (not the cached one from module load)
            const sidebarPath = API_SIDEBAR_PATH;
            let freshSidebar: any[] = [];

            if (fs.existsSync(sidebarPath)) {
              try {
                const sidebarModule = require("./api-docs/embedded-api/sidebar.ts");
                freshSidebar = sidebarModule.default || sidebarModule;
                console.log("Loaded fresh sidebar from generated files");
              } catch (sidebarError: any) {
                console.warn(
                  "Could not load fresh sidebar, using empty array:",
                  sidebarError.message,
                );
                freshSidebar = [];
              }
            } else {
              console.warn(
                "Generated sidebar file not found, using empty array",
              );
              freshSidebar = [];
            }

            const allowedTags = data.tags?.map((tag: any) => tag["name"]) || [];

            // Use freshly loaded sidebar items from the generated file
            const sidebarItems = Array.isArray(freshSidebar)
              ? freshSidebar
              : [];

            const filteredItems = sidebarItems.filter((item: any) => {
              if (item.type !== "category") {
                return true;
              }

              return allowedTags.includes(item.label);
            });

            return filteredItems;
          } catch (error: any) {
            console.warn(
              "Error loading embedded API spec from cache:",
              error.message,
            );
            return [];
          }
        },
      },
    ],
    [
      "docusaurus-plugin-openapi-docs",
      {
        id: "embedded-api",
        docsPluginId: "embedded-api",
        config: {
          embedded: {
            specPath: "src/data/embedded_api_spec.json",
            outputDir: "api-docs/embedded-api",
            sidebarOptions: {
              groupPathsBy: "tag",
              categoryLinkSource: "tag",
              sidebarCollapsed: false,
              sidebarCollapsible: false,
            },
          },
        },
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
          excludeRoutes: ["./api-docs/**"],
        },
      } satisfies LLmPluginOptions,
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

  themeConfig: {
    colorMode: {
      disableSwitch: false,
    },
    mermaid: {
      theme: {
        light: "base",
        dark: "base",
      },
      options: {
        themeVariables: {
          primaryColor: "#5F5CFF",
          primaryTextColor: "#FFFFFF",
          primaryBorderColor: "#1A194D",
          secondaryColor: "#FF6A4D",
          tertiaryColor: "#E8EAF6",
          tertiaryTextColor: "#000000",
          tertiaryBorderColor: "#E8EAF6",
          background: "#FFFFFF",
          clusterBkg: "#F5F5F5",
          fontFamily: "var(--ifm-font-family-base)",
        },
        flowchart: {
          rankSpacing: 100,
          subGraphTitleMargin: 10,
          nodeSpacing: 100,
        },
      },
    },
    docs: {
      sidebar: {
        autoCollapseCategories: true,
      },
    },
    algolia: {
      appId: "OYKDBC51MU",
      apiKey: "15c487fd9f7722282efd8fcb76746fce",
      indexName: "airbyte",
    },
    announcementBar: {
      id: "try_airbyte_cloud",
      content:
        '<a target="_blank" rel="noopener noreferrer" href="https://cloud.airbyte.io/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=NavBar">Try Airbyte Cloud</a>! Free for 30 days, no credit card needed.',
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
          docsPluginId: "ai-agents",
          sidebarId: "ai-agents",
          label: "AI Agents",
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
          dropdownActiveClassDisabled: true,
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
  },
};

export default config;
