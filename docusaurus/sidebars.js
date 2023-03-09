const fs = require("fs");
const path = require("path")

const connectorsDocsRoot = "../docs/integrations";
const sourcesDocs = `${connectorsDocsRoot}/sources`;
const destinationDocs = `${connectorsDocsRoot}/destinations`;

function getFilenamesInDir(prefix, dir, excludes) {
    return fs.readdirSync(dir)
        .filter(fileName => !fileName.endsWith(".inapp.md"))
        .map(fileName => fileName.replace(".md", ""))
        .filter(fileName => excludes.indexOf(fileName.toLowerCase()) === -1)
        .map(filename => {
            return {type: 'doc', id: path.join(prefix, filename)}
        });
}

function getSourceConnectors() {
    return getFilenamesInDir("integrations/sources/", sourcesDocs, ["readme"]);
}

function getDestinationConnectors() {
    return getFilenamesInDir("integrations/destinations/", destinationDocs, ["readme"]);
}
module.exports = {
  mySidebar: [
    {
      type: 'doc',
      label: 'Start here',
      id: "readme",
    },
    {
      type: 'category',
      label: 'Connector Catalog',
      link: {
        type: 'doc',
        id: 'integrations/README',
      },
      items: [
          {
            type: 'category',
            label: 'Sources',
            link: {
              type: 'generated-index',
            },
            items: getSourceConnectors()
          },
          {
            type: 'category',
            label: 'Destinations',
            link: {
              type: 'generated-index',
            },
            items: getDestinationConnectors()
          },
          {
            type: 'doc',
            id: "integrations/custom-connectors",
          },
        ]

      },
    {
      type: 'category',
      label: 'Airbyte Cloud',
      items: [
        {
          type: 'doc',
          label: 'Getting Started',
          id: "cloud/getting-started-with-airbyte-cloud",
        },
        'cloud/core-concepts',
        'cloud/managing-airbyte-cloud',
        'cloud/dbt-cloud-integration',
      ],
    },
    {
      type: 'category',
      label: 'Airbyte Open Source Quick Start',
      link: {
        type: 'generated-index',
      },
      items: [
        'quickstart/deploy-airbyte',
        'quickstart/add-a-source',
        'quickstart/add-a-destination',
        'quickstart/set-up-a-connection',
      ],
    },
    {
      type: 'category',
      label: 'Deploy Airbyte Open Source',
      link: {
        type: 'generated-index',
      },
      items: [
        {
          type: 'doc',
          label: 'On your local machine',
          id: 'deploying-airbyte/local-deployment',
        },
        {
          type: 'doc',
          label: 'On AWS EC2',
          id: 'deploying-airbyte/on-aws-ec2',
        },
        
        {
          type: 'doc',
          label: 'On Azure',
          id:'deploying-airbyte/on-azure-vm-cloud-shell',
        },
        {
          type: 'doc',
          label: 'On Google (GCP)',
          id:'deploying-airbyte/on-gcp-compute-engine',
        },
        {
          type: 'doc',
          label: 'On Kubernetes',
          id:'deploying-airbyte/on-kubernetes',
        },
        {
          type: 'doc',
          label: 'On Kubernetes using Helm',
          id:'deploying-airbyte/on-kubernetes-via-helm',
        },
        {
          type: 'doc',
          label: 'On Restack',
          id:'deploying-airbyte/on-restack',
        },
        {
          type: 'doc',
          label: 'On Plural',
          id:'deploying-airbyte/on-plural',
        },
        {
          type: 'doc',
          label: 'On Oracle Cloud',
          id:'deploying-airbyte/on-oci-vm',
        },
        {
          type: 'doc',
          label: 'On DigitalOcean',
          id:'deploying-airbyte/on-digitalocean-droplet',
        },
      ],
    },
    {
      type: 'category',
      label: 'Manage Airbyte Open Source',
      link: {
        type: 'generated-index',
      },
      items: [
        'operator-guides/upgrading-airbyte',
        'operator-guides/reset',
        'operator-guides/configuring-airbyte-db',
        'operator-guides/configuring-connector-resources',
        'operator-guides/browsing-output-logs',
        'operator-guides/using-the-airflow-airbyte-operator',
        'operator-guides/using-prefect-task',
        'operator-guides/using-dagster-integration',
        'operator-guides/locating-files-local-destination',
        {
          type: 'category',
          label: 'Transformations and Normalization',
          items: [
            'operator-guides/transformation-and-normalization/transformations-with-sql',
            'operator-guides/transformation-and-normalization/transformations-with-dbt',
            'operator-guides/transformation-and-normalization/transformations-with-airbyte',
            ]
          },
          {
            type: 'category',
            label: 'Configuring Airbyte',
            link: {
              type: 'doc',
              id: 'operator-guides/configuring-airbyte',
            },
            items: [
                'operator-guides/sentry-integration',
              ]
          },
        'operator-guides/using-custom-connectors',
        'operator-guides/scaling-airbyte',
        'operator-guides/configuring-sync-notifications',
        'operator-guides/collecting-metrics',
      ],
    },
    {
      type: 'category',
      label: 'Troubleshoot Airbyte',
      items: [
        'troubleshooting/README',
        'troubleshooting/on-deploying',
        'troubleshooting/new-connection',
        'troubleshooting/running-sync',     
      ],
    },
    {
      type: 'category',
      label: 'Build a connector',      
      items: [
        {
          type: 'doc',
          label: 'CDK Introduction',
          id: 'connector-development/README',
        },
        {
          type: 'category',
          label: 'Low-code connector development',
          items: [
            'connector-development/config-based/connector-builder-ui',
            {
              label: 'Low-code CDK Intro',
              type: 'doc',
              id: 'connector-development/config-based/low-code-cdk-overview',
            },
            {
              type: 'category',
              label: 'Tutorial',
              items: [
                'connector-development/config-based/tutorial/getting-started',
                'connector-development/config-based/tutorial/create-source',
                'connector-development/config-based/tutorial/install-dependencies',
                'connector-development/config-based/tutorial/connecting-to-the-API-source',
                'connector-development/config-based/tutorial/reading-data',
                'connector-development/config-based/tutorial/incremental-reads',
                'connector-development/config-based/tutorial/testing',
              ],
            },
            {
              type: 'category',
              label: 'Understanding the YAML file',
              link: {
                type: 'doc',
                id: 'connector-development/config-based/understanding-the-yaml-file/yaml-overview',
              },
              items: [
                {
                  type: `category`,
                  label: `Requester`,
                  link: {
                    type: 'doc',
                    id: 'connector-development/config-based/understanding-the-yaml-file/requester',
                  },
                  items: [
                    'connector-development/config-based/understanding-the-yaml-file/request-options',
                    'connector-development/config-based/understanding-the-yaml-file/authentication',
                    'connector-development/config-based/understanding-the-yaml-file/error-handling',  
                  ]
              },
                'connector-development/config-based/understanding-the-yaml-file/pagination',
                'connector-development/config-based/understanding-the-yaml-file/record-selector',
                'connector-development/config-based/understanding-the-yaml-file/stream-slicers',
                'connector-development/config-based/understanding-the-yaml-file/reference',
              ]
            },
            'connector-development/config-based/advanced-topics',    
          ]
        },
        'connector-development/tutorials/cdk-speedrun',
        {
          type: 'category',
          label: 'Python CDK: Creating a HTTP API Source',
          items: [
            'connector-development/tutorials/cdk-tutorial-python-http/getting-started',
            'connector-development/tutorials/cdk-tutorial-python-http/creating-the-source',
            'connector-development/tutorials/cdk-tutorial-python-http/install-dependencies',
            'connector-development/tutorials/cdk-tutorial-python-http/define-inputs',
            'connector-development/tutorials/cdk-tutorial-python-http/connection-checking',
            'connector-development/tutorials/cdk-tutorial-python-http/declare-schema',
            'connector-development/tutorials/cdk-tutorial-python-http/read-data',
            'connector-development/tutorials/cdk-tutorial-python-http/use-connector-in-airbyte',
            'connector-development/tutorials/cdk-tutorial-python-http/test-your-connector',
          ]
        },
        'connector-development/tutorials/building-a-python-source',
        'connector-development/tutorials/building-a-python-destination',
        'connector-development/tutorials/building-a-java-destination',
        'connector-development/tutorials/profile-java-connector-memory',
        {
          type: 'category',
          label: 'Connector Development Kit (Python)',
          link: {
            type: 'doc',
            id: 'connector-development/cdk-python/README',
          },
          items: [
            'connector-development/cdk-python/basic-concepts',
            'connector-development/cdk-python/schemas',
            'connector-development/cdk-python/full-refresh-stream',
            'connector-development/cdk-python/incremental-stream',
            'connector-development/cdk-python/http-streams',
            'connector-development/cdk-python/python-concepts',
            'connector-development/cdk-python/stream-slices',
          ]
        },
        'connector-development/cdk-faros-js',
        'connector-development/airbyte101',
        'connector-development/testing-connectors/README',
        'connector-development/testing-connectors/source-acceptance-tests-reference',
        'connector-development/connector-specification-reference',
        'connector-development/best-practices',
        'connector-development/ux-handbook',
      ]
    },
    {
      type: 'category',
      label: 'Contribute to Airbyte',
      items: [
        'contributing-to-airbyte/README',
        'contributing-to-airbyte/code-of-conduct',
        'contributing-to-airbyte/maintainer-code-of-conduct',
        'contributing-to-airbyte/developing-locally',
        'contributing-to-airbyte/developing-on-docker',
        'contributing-to-airbyte/developing-on-kubernetes',
        'contributing-to-airbyte/monorepo-python-development',
        'contributing-to-airbyte/code-style',
        'contributing-to-airbyte/issues-and-pull-requests',
        'contributing-to-airbyte/gradle-cheatsheet',
        'contributing-to-airbyte/gradle-dependency-update',
        {
          type: 'category',
          label: 'Updating documentation',
          link: {
            type: 'doc',
            id: 'contributing-to-airbyte/updating-documentation',
          },
          items: [
            {
              type: 'link',
              label: 'Connector doc template',
              href: 'https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw',
            },
          ]
        },
      ]
    },
    {
      type: 'category',
      label: 'Understand Airbyte',
      items: [
        'understanding-airbyte/beginners-guide-to-catalog',
        'understanding-airbyte/airbyte-protocol',
        'understanding-airbyte/airbyte-protocol-docker',
        'understanding-airbyte/basic-normalization',
        {
          type: 'category',
          label: 'Connections and Sync Modes',
          items: [
            {
              type: 'doc',
              label: 'Connections Overview',
              id: "understanding-airbyte/connections/README",
            },
            'understanding-airbyte/connections/full-refresh-overwrite',
            'understanding-airbyte/connections/full-refresh-append',
            'understanding-airbyte/connections/incremental-append',
            'understanding-airbyte/connections/incremental-deduped-history',
          ]
        },
        'understanding-airbyte/operations',
        'understanding-airbyte/high-level-view',
        'understanding-airbyte/jobs',
        'understanding-airbyte/tech-stack',
        'understanding-airbyte/cdc',
        'understanding-airbyte/namespaces',
        'understanding-airbyte/supported-data-types',
        'understanding-airbyte/json-avro-conversion',
        'understanding-airbyte/database-data-catalog',
      ]
    },
    {
      type: 'doc',
      id: "operator-guides/security",
    },
    {
      type: 'doc',
      id: "api-documentation",
    },
    {
      type: 'link',
      label: 'CLI documentation',
      href: 'https://github.com/airbytehq/airbyte/blob/master/octavia-cli/README.md',
    },
    {
      type: 'category',
      label: 'Project Overview',
      items: [
        {
          type: 'link',
          label: 'Roadmap',
          href: 'https://app.harvestr.io/roadmap/view/pQU6gdCyc/airbyte-roadmap',
        },
        'project-overview/product-release-stages',
        'project-overview/slack-code-of-conduct',
        {
          type: 'link',
          label: 'Airbyte Repository',
          href: 'https://github.com/airbytehq/airbyte',
        },
        {
          type: 'category',
          label: 'Licenses',
          link: {
            type: 'doc',
            id: 'project-overview/licenses/README',
          },
          items: [
            'project-overview/licenses/license-faq',
            'project-overview/licenses/elv2-license',
            'project-overview/licenses/mit-license',
            'project-overview/licenses/examples',
          ]
        },
      ],
    },
    {
      type: 'category',
      label: 'Release Notes',
      link: {
        type: 'generated-index',
      },
      items: [
        'release_notes/december_2022',
        'release_notes/november_2022',
        'release_notes/october_2022',
        'release_notes/september_2022',
        'release_notes/august_2022',
        'release_notes/july_2022',
      ],
    },
  ],
}
