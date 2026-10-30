import "dotenv/config.js";
import type { Config } from "@docusaurus/types";
import { themes as prismThemes } from "prism-react-renderer";
import type { Options as ClassicPresetOptions } from "@docusaurus/preset-classic";
import { PluginOptions as LLmPluginOptions } from "@signalwire/docusaurus-plugin-llms-txt";

// Import remark plugins - lazy load to prevent webpack from bundling Node.js code
const getRemarkPlugins = () => ({
  docsHeaderDecoration: require("./src/remark/docsHeaderDecoration"),
  enterpriseDocsHeaderInformation: require("./src/remark/enterpriseDocsHeaderInformation"),
  productInformation: require("./src/remark/productInformation"),
  connectorList: require("./src/remark/connectorList"),
  specDecoration: require("./src/remark/specDecoration"),
  docMetaTags: require("./src/remark/docMetaTags"),
  addButtonToTitle: require("./src/remark/addButtonToTitle"),
});

const plugins = getRemarkPlugins();

const lightCodeTheme = prismThemes.github;
const darkCodeTheme = prismThemes.dracula;

const config: Config = {
  future: {
    v4: true,
    faster: true,
  },
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: "throw",
    },
    mdx1Compat: {
      comments: true,
      admonitions: true,
      headingIds: true,
    },
  },
  themes: [
    "@docusaurus/theme-mermaid",
    "@saucelabs/theme-github-codeblock",
  ],
  title: "Airbyte Docs",
  tagline:
    "Airbyte is an open-source data integration platform to build ELT pipelines. Consolidate your data in your data warehouses, lakes and databases.",
  url: "https://docs.airbyte.com/",
  // Assumed relative path.  If you are using airbytehq.github.io use /
  // anything else should match the repo name
  baseUrl: "/",
  trailingSlash: false,
  onBrokenLinks: "throw",

  favicon: "img/favicon.png",
  organizationName: "airbytehq", // Usually your GitHub org/user name.
  projectName: "airbyte", // Usually your repo name.

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
    // disables concatenateModules optimization for dev and for prod server builds to improve build times - more info: https://github.com/facebook/docusaurus/discussions/11199
    function disableExpensiveBundlerOptimizationPlugin() {
      return {
        name: "disable-expensive-bundler-optimizations",
        configureWebpack(_config, isServer) {
          return {
            optimization: {
              concatenateModules: false,
            },
          };
        },
      };
    },
    // This plugin controls "platform" docs (no longer versioned)
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "platform",
        path: "../docs/platform",
        routeBasePath: "/platform",
        sidebarPath: "./sidebar-platform.js",
        editUrl:
          "https://github.com/airbytehq/airbyte/blob/master/docs",
        remarkPlugins: [
          plugins.productInformation,
          plugins.addButtonToTitle,
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
          plugins.productInformation,
          plugins.addButtonToTitle,
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
        beforeDefaultRemarkPlugins: [
          plugins.specDecoration,
          plugins.connectorList,
        ], // use before-default plugins so TOC rendering picks up inserted headings
        remarkPlugins: [
          plugins.docsHeaderDecoration,
          plugins.enterpriseDocsHeaderInformation,
          plugins.productInformation,
          plugins.docMetaTags,
        ],
      },
    ],
    // This plugin controls Developers docs, which are not versioned
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "developers",
        path: "../docs/developers",
        routeBasePath: "/developers",
        sidebarPath: "./sidebar-developers.js",
        editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
        remarkPlugins: [
          plugins.productInformation,
          plugins.addButtonToTitle,
        ],
      },
    ],
    // This plugin controls Community docs, which are not versioned
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "community",
        path: "../docs/community",
        routeBasePath: "/community",
        sidebarPath: "./sidebar-community.js",
        editUrl: "https://github.com/airbytehq/airbyte/blob/master/docs",
        remarkPlugins: [
          plugins.productInformation,
          plugins.addButtonToTitle,
        ],
      },
    ],
    require.resolve("./src/plugins/enterpriseConnectors"),
    require.resolve("./src/plugins/agentConnectors"),
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
      configureWebpack(config, isServer) {
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
          ignoreWarnings: [
            (warning) => {
              const msg = String(warning?.message || "");
              return (
                /Can't resolve ['"]bufferutil['"]/.test(msg) ||
                /Can't resolve ['"]utf-8-validate['"]/.test(msg)
              );
            },
          ],
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
    require.resolve("./src/scripts/kapaWithDataGrailConsent.js"),
  ],

  themeConfig: {
    // Default social card for og:image/twitter:image on every page. Per-page
    // front matter `image` still takes precedence.
    image: "img/airbyte-docs-social-card.png",
    metadata: [
      // Docs pages override this with "article" in src/theme/DocItem/Metadata.
      { property: "og:type", content: "website" },
      { property: "og:image:width", content: "1200" },
      { property: "og:image:height", content: "630" },
      { property: "og:image:alt", content: "Airbyte Documentation" },
    ],
    colorMode: {
      disableSwitch: false,
    },
    mermaid: {
      theme: {
        light: "default",
        dark: "dark",
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
        '<a target="_blank" rel="noopener noreferrer" href="https://cloud.airbyte.com/signup?utm_source=docs&utm_medium=banner&utm_campaign=airbyte_cloud_docs_banner">Try Airbyte Cloud!</a> Free trial for 14 days, no credit card needed.',
      backgroundColor: "#615eff",
      textColor: "#ffffff",
      isCloseable: false,
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
          docsPluginId: "developers",
          sidebarId: "developers",
          label: "Developers",
        },
        {
          type: "docSidebar",
          position: "left",
          docsPluginId: "community",
          sidebarId: "community",
          label: "Community",
        },
        {
          href: "https://status.airbyte.com",
          label: "Status",
          className: "cloudStatusLink",
        },
        // --- Right side ---
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
