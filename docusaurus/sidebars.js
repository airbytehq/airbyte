const fs = require('fs');
const path = require('path');

const connectorsDocsRoot = '../docs/integrations';
const sourcesDocs = `${connectorsDocsRoot}/sources`;
const destinationDocs = `${connectorsDocsRoot}/destinations`;

function getFilenamesInDir(prefix, dir, excludes) {
  return fs
    .readdirSync(dir)
    .filter((fileName) => !(fileName.endsWith('.inapp.md') || fileName.endsWith('-migrations.md')))
    .map((fileName) => fileName.replace('.md', ''))
    .filter((fileName) => excludes.indexOf(fileName.toLowerCase()) === -1)
    .map((filename) => {
      return { type: 'doc', id: path.join(prefix, filename) };
    });
}

function getSourceConnectors() {
  return getFilenamesInDir('integrations/sources/', sourcesDocs, ['readme']);
}

function getDestinationConnectors() {
  return getFilenamesInDir('integrations/destinations/', destinationDocs, [
    'readme',
  ]);
}

const sectionHeader = (title) => ({
  type: 'html',
  value: title,
  className: 'navbar__category',
});

const buildAConnector = {
  type: 'category',
  label: 'Build a Connector',
  items: [
    {
      type: 'doc',
      label: 'Overview',
      id: 'connector-development/README',
    },
    {
      type: 'category',
      label: 'Connector Builder',
      items: [
        'connector-development/connector-builder-ui/overview',
        'connector-development/connector-builder-ui/connector-builder-compatibility',
        'connector-development/connector-builder-ui/tutorial',
        {
          type: 'category',
          label: 'Concepts',
          items: [
            'connector-development/connector-builder-ui/authentication',
            'connector-development/connector-builder-ui/record-processing',
            'connector-development/connector-builder-ui/pagination',
            'connector-development/connector-builder-ui/incremental-sync',
            'connector-development/connector-builder-ui/partitioning',
            'connector-development/connector-builder-ui/error-handling',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Low-code connector development',
      items: [
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
              ],
            },
            'connector-development/config-based/understanding-the-yaml-file/incremental-syncs',
            'connector-development/config-based/understanding-the-yaml-file/pagination',
            'connector-development/config-based/understanding-the-yaml-file/partition-router',
            'connector-development/config-based/understanding-the-yaml-file/record-selector',
            'connector-development/config-based/understanding-the-yaml-file/reference',
          ],
        },
        'connector-development/config-based/advanced-topics',
      ],
    },

    {
      type: 'category',
      label: 'Connector Development Kit',
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
      ],
    },
    {
      type: 'category',
      label: 'Testing Connectors',
      link: {
        type: 'doc',
        id: 'connector-development/testing-connectors/README',
      },
      items: [
        'connector-development/testing-connectors/connector-acceptance-tests-reference',
        'connector-development/testing-connectors/testing-a-local-catalog-in-development',
      ],
    },
    {
      type: 'category',
      label: 'Tutorials',
      items: [
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
          ],
        },
        'connector-development/tutorials/building-a-python-source',
        'connector-development/tutorials/building-a-python-destination',
        'connector-development/tutorials/building-a-java-destination',
        'connector-development/tutorials/profile-java-connector-memory',
      ],
    },
    'connector-development/connector-specification-reference',
    'connector-development/schema-reference',
    'connector-development/connector-metadata-file',
    'connector-development/best-practices',
    'connector-development/ux-handbook',
  ],
};

const connectorCatalog = {
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
      items: getSourceConnectors(),
    },
    {
      type: 'category',
      label: 'Destinations',
      link: {
        type: 'generated-index',
      },
      items: getDestinationConnectors(),
    },
    {
      type: 'doc',
      id: 'integrations/custom-connectors',
    },
  ],
};

const contributeToAirbyte = {
  type: 'category',
  label: 'Contribute to Airbyte',
  link: {
    type: 'doc',
    id: 'contributing-to-airbyte/README',
  },
  items: [
    'contributing-to-airbyte/code-of-conduct',
    'contributing-to-airbyte/issues-and-pull-requests',
    'contributing-to-airbyte/developing-locally',
    'contributing-to-airbyte/developing-on-docker',
    'contributing-to-airbyte/python-gradle-setup',
    'contributing-to-airbyte/code-style',
    'contributing-to-airbyte/gradle',
    {
      type: 'category',
      label: 'Updating documentation',
      link: {
        type: 'doc',
        id: 'contributing-to-airbyte/contribute-documentation',
      },
      items: [
        {
          type: 'link',
          label: 'Connector doc template',
          href: 'https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw',
        },
      ],
    },
  ],
};

const airbyteCloud = [
  {
    type: 'doc',
    label: 'Getting Started',
    id: 'cloud/getting-started-with-airbyte-cloud',
  },
  'cloud/core-concepts',
  {
    type: 'category',
    label: 'Using Airbyte Cloud',
    link: {
      type: 'generated-index',
    },
    items: [
      'cloud/managing-airbyte-cloud/edit-stream-configuration',
      'cloud/managing-airbyte-cloud/manage-schema-changes',
      'cloud/managing-airbyte-cloud/manage-data-residency',
      'cloud/managing-airbyte-cloud/manage-credits',
      'cloud/managing-airbyte-cloud/review-sync-summary',
      'cloud/managing-airbyte-cloud/manage-airbyte-cloud-notifications',
      'cloud/managing-airbyte-cloud/dbt-cloud-integration',
      'cloud/managing-airbyte-cloud/manage-airbyte-cloud-workspace',
      'cloud/managing-airbyte-cloud/understand-airbyte-cloud-limits',
      'cloud/managing-airbyte-cloud/review-connection-state',
    ],
  },
];

const ossGettingStarted = {
  type: 'category',
  label: 'Getting Started',
  link: {
    type: 'generated-index',
  },
  items: [
    'quickstart/deploy-airbyte',
    'quickstart/add-a-source',
    'quickstart/add-a-destination',
    'quickstart/set-up-a-connection',
  ],
};

const deployAirbyte = {
  type: 'category',
  label: 'Deploy Airbyte',
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
      id: 'deploying-airbyte/on-azure-vm-cloud-shell',
    },
    {
      type: 'doc',
      label: 'On Google (GCP)',
      id: 'deploying-airbyte/on-gcp-compute-engine',
    },
    {
      type: 'doc',
      label: 'On Kubernetes using Kustomize',
      id: 'deploying-airbyte/on-kubernetes',
    },
    {
      type: 'doc',
      label: 'On Kubernetes using Helm',
      id: 'deploying-airbyte/on-kubernetes-via-helm',
    },
    {
      type: 'doc',
      label: 'On Restack',
      id: 'deploying-airbyte/on-restack',
    },
    {
      type: 'doc',
      label: 'On Plural',
      id: 'deploying-airbyte/on-plural',
    },
    {
      type: 'doc',
      label: 'On Oracle Cloud',
      id: 'deploying-airbyte/on-oci-vm',
    },
    {
      type: 'doc',
      label: 'On DigitalOcean',
      id: 'deploying-airbyte/on-digitalocean-droplet',
    },
  ],
};

const operatorGuide = {
  type: 'category',
  label: 'Manage Airbyte',
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
      ],
    },
    'operator-guides/configuring-airbyte',
    'operator-guides/using-custom-connectors',
    'operator-guides/scaling-airbyte',
    'operator-guides/configuring-sync-notifications',
  ],
};

const understandingAirbyte = {
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
          id: 'understanding-airbyte/connections/README',
        },
        'understanding-airbyte/connections/full-refresh-overwrite',
        'understanding-airbyte/connections/full-refresh-append',
        'understanding-airbyte/connections/incremental-append',
        'understanding-airbyte/connections/incremental-deduped-history',
      ],
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
  ],
};

const security = {
  type: 'doc',
  id: 'operator-guides/security',
};

const support = {
  type: 'doc',
  id: 'operator-guides/contact-support',
};

module.exports = {
  mySidebar: [
    {
      type: 'doc',
      label: 'Start here',
      id: 'readme',
    },
    sectionHeader('Airbyte Connectors'),
    connectorCatalog,
    buildAConnector,
    sectionHeader('Airbyte Cloud'),
    ...airbyteCloud,
    sectionHeader('Airbyte Open Source (OSS)'),
    ossGettingStarted,
    deployAirbyte,
    operatorGuide,
    {
      type: 'doc',
      id: 'troubleshooting',
    },
    sectionHeader('Developer Guides'),
    {
      type: 'doc',
      id: 'api-documentation',
    },
    {
      type: 'doc',
      id: 'cli-documentation',
    },
    understandingAirbyte,
    contributeToAirbyte,
    sectionHeader('Resources'),
    support,
    security,
    {
      type: 'category',
      label: 'Project Overview',
      items: [
        {
          type: 'link',
          label: 'Roadmap',
          href: 'https://go.airbyte.com/roadmap',
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
          ],
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
        /*
        {
              type: 'category',
              label: 'May 2023',
              link: {
                  type: 'doc',
                  id: 'release_notes/may_2023',
              },
              items: [
                'release_notes/upgrading_to_destinations_v2'
              ],
        },
        */
        'release_notes/may_2023',
        'release_notes/april_2023',
        'release_notes/march_2023',
        'release_notes/february_2023',
        'release_notes/january_2023',
        'release_notes/december_2022',
        'release_notes/november_2022',
        'release_notes/october_2022',
        'release_notes/september_2022',
        'release_notes/august_2022',
        'release_notes/july_2022',
      ],
    },
  ],
};
