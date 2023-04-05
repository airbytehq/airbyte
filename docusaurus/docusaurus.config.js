// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: 'Airbyte Documentation',
    tagline:
        'Airbyte is an open-source data integration platform to build ELT pipelines. Consolidate your data in your data warehouses, lakes and databases.',
    url: 'https://docs.airbyte.com/',
    // Assumed relative path.  If you are using airbytehq.github.io use /
    // anything else should match the repo name
    baseUrl: '/',
    onBrokenLinks: 'throw',
    onBrokenMarkdownLinks: 'throw',
    favicon: 'img/favicon.png',
    organizationName: 'airbytehq', // Usually your GitHub org/user name.
    projectName: 'airbyte', // Usually your repo name.

    plugins:    [
                  [
                    '@docusaurus/plugin-client-redirects',
                    {
                      fromExtensions: ['html', 'htm'], // /myPage.html -> /myPage
                      redirects: [
                        // /docs/oldDoc -> /docs/newDoc
                        {
                          from: '/upgrading-airbyte',
                          to: '/operator-guides/upgrading-airbyte',
                        },
                        {
                            from: '/catalog',
                            to: '/understanding-airbyte/airbyte-protocol',
                        },
                        {
                            from: '/integrations/sources/google-analytics-data-api',
                            to: '/integrations/sources/google-analytics-v4',
                        },
                        {
                            from: '/integrations/sources/appstore',
                            to: '/integrations/sources/appstore-singer',
                        },
                        {
                            from: '/project-overview/security',
                            to: '/operator-guides/security',
                        },
                        {
                            from: '/operator-guides/securing-airbyte',
                            to: '/operator-guides/security',
                        },
                        {
                            from: '/connector-development/config-based/',
                            to: '/connector-development/config-based/low-code-cdk-overview',
                        },
                        {
                            from: '/project-overview/changelog',
                            to: '/category/release-notes',
                        },
                        {
                            from: '/connector-development/config-based/understanding-the-yaml-file/stream-slicers/',
                            to: '/connector-development/config-based/understanding-the-yaml-file/partition-router',
                        },
                        {
                            from: '/cloud/managing-airbyte-cloud',
                            to: '/category/using-airbyte-cloud',
                        },
                        {
                            from: '/category/managing-airbyte-cloud',
                            to: '/category/using-airbyte-cloud'
                        },
                        {
                            from: '/cloud/dbt-cloud-integration',
                            to: '/cloud/managing-airbyte-cloud/dbt-cloud-integration',
                        },
//                        {
//                         from: '/some-lame-path',
//                         to: '/a-much-cooler-uri',
//                        },
                      ],
                    },
                  ],
                ],

    presets: [
        [
            'classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    routeBasePath: '/',
                    sidebarCollapsible: true,
                    sidebarPath: require.resolve('./sidebars.js'),
                    editUrl: 'https://github.com/airbytehq/airbyte/blob/master/docs',
                    path: '../docs',
                    exclude: ['**/*.inapp.md'],
                },
                blog: false,
                theme: {
                    customCss: require.resolve('./src/css/custom.css'),
                },
                gtag: {
                    trackingID: 'UA-156258629-2',
                    anonymizeIP: true,
                },
            }),
        ],
    ],

    scripts: [
        {
            src: 'https://cdn.jsdelivr.net/gh/RelevanceAI/ask-relevance-widget@latest/dist/bundle.min.js',
            defer: true,
            config: 'eyJ1cmwiOiJodHRwczovL2FwaS1iY2JlNWEuc3RhY2sudHJ5cmVsZXZhbmNlLmNvbS9sYXRlc3QvZGF0YXNldHMvYWlyYnl0ZS1naXRodWIvc2ltcGxlX3NlYXJjaCIsImZpZWxkIjoiZmlsZV9jb250ZW50X3BsYWluIiwidmVjdG9yX2ZpZWxkIjoiZmlsZV9jb250ZW50X3BsYWluX29wZW5haV90ZXh0LWVtYmVkZGluZy1hZGEtMDAyX3ZlY3Rvcl8iLCJtb2RlbCI6InRleHQtZW1iZWRkaW5nLWFkYS0wMDIiLCJhdXRoX2hlYWRlciI6ImUyZmE5NjE4M2M5Mi00N2Y2LTk1YjMtZjRiOWUwZmFjMTMyOk5HVTFORGRtTkRBdE1HSTVPQzAwTmpFNUxXRXhZVGN0T0dNMFpUZGlOekE1TXpoaSIsInJlZmVyZW5jZV90aXRsZV9maWVsZCI6InRpdGxlIiwicmVmZXJlbmNlX3VybF9maWVsZCI6InVybCIsInNob3dEb2N1bWVudHMiOnRydWUsImhlYWRsZXNzIjp0cnVlLCJrZXl3b3JkTW9kZSI6dHJ1ZSwiZG9jdW1lbnRzUGFnZVNpemUiOjUsInN0b3JlUXVlcmllcyI6dHJ1ZX0='
        }
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
            navbar: {
                title: '',
                logo: {
                    alt: 'Simple, secure and extensible data integration',
                    src: 'img/logo-dark.png',
                    srcDark: 'img/logo-light.png',
                    width: 140,
                    height: 40,
                },
                items: [
                    {
                        href: 'https://airbyte.io/',
                        position: 'left',
                        label: 'Home',
                    },
                    {
                        href: 'https://status.airbyte.io/',
                        label: 'Status',
                        position: 'left',
                    },
                    {
                        href: 'https://airbyte.com/tutorials',
                        label: 'Tutorials',
                        position: 'left',
                    },
                    {
                        href: 'https://discuss.airbyte.io/',
                        label: 'Support',
                        position: 'left',
                    },
                    {
                        href: 'https://cloud.airbyte.io/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=NavBar',
                        label: 'Try Airbyte Cloud',
                        position: 'left',
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
