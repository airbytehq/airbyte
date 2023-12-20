const fs = require("fs");
const path = require("path");
const {
  parseMarkdownContentTitle,
  parseFrontMatter,
} = require("@docusaurus/utils");

const connectorsDocsRoot = "../docs/integrations";
const sourcesDocs = `${connectorsDocsRoot}/sources`;
const destinationDocs = `${connectorsDocsRoot}/destinations`;

function getFilenamesInDir(prefix, dir, excludes) {
  return fs
    .readdirSync(dir)
    .filter(
      (fileName) =>
        !(
          fileName.endsWith(".inapp.md") ||
          fileName.endsWith("-migrations.md") ||
          fileName.endsWith(".js")
        )
    )
    .map((fileName) => fileName.replace(".md", ""))
    .filter((fileName) => excludes.indexOf(fileName.toLowerCase()) === -1)
    .map((filename) => {
      // Get the first header of the markdown document
      const { contentTitle } = parseMarkdownContentTitle(
        parseFrontMatter(fs.readFileSync(path.join(dir, `${filename}.md`)))
          .content
      );
      if (!contentTitle) {
        throw new Error(
          `Could not parse title from ${path.join(
            prefix,
            filename
          )}. Make sure there's no content above the first heading!`
        );
      }

      // If there is a migration doc for this connector nest this under the original doc as "Migration Guide"
      const migrationDocPath = path.join(dir, `${filename}-migrations.md`);
      if (fs.existsSync(migrationDocPath)) {
        return {
          type: "category",
          label: contentTitle,
          link: { type: "doc", id: path.join(prefix, filename) },
          items: [
            {
              type: "doc",
              id: path.join(prefix, `${filename}-migrations`),
              label: "Migration Guide",
            },
          ],
        };
      }

      return { type: "doc", id: path.join(prefix, filename), label: contentTitle };
    });
}

function getSourceConnectors() {
  return getFilenamesInDir("integrations/sources/", sourcesDocs, [
    "readme",
    "postgres",
    "mysql"
  ]);
}

function getDestinationConnectors() {
  return getFilenamesInDir("integrations/destinations/", destinationDocs, [
    "readme",
  ]);
}

const sourcePostgres = {
  type: "category",
  label: "Postgres",
  link: {
    type: "doc",
    id: "integrations/sources/postgres",
  },
  items: [
    {
      type: "doc",
      label: "Cloud SQL for Postgres",
      id: "integrations/sources/postgres/cloud-sql-postgres",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "integrations/sources/postgres/postgres-troubleshooting",
    },
  ],
};

const sourceMysql = {
  type: "category",
  label: "MySQL",
  link: {
    type: "doc",
    id: "integrations/sources/mysql",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "integrations/sources/mysql/mysql-troubleshooting",
    },
  ],
};

const sectionHeader = (title) => ({
  type: "html",
  value: title,
  className: "navbar__category",
});

const buildAConnector = {
  type: "category",
  label: "Build a Connector",
  items: [
    {
      type: "doc",
      label: "Overview",
      id: "connector-development/README",
    },
    {
      type: "category",
      label: "Connector Builder",
      items: [
        "connector-development/connector-builder-ui/overview",
        "connector-development/connector-builder-ui/connector-builder-compatibility",
        "connector-development/connector-builder-ui/tutorial",
        {
          type: "category",
          label: "Concepts",
          items: [
            "connector-development/connector-builder-ui/authentication",
            "connector-development/connector-builder-ui/record-processing",
            "connector-development/connector-builder-ui/pagination",
            "connector-development/connector-builder-ui/incremental-sync",
            "connector-development/connector-builder-ui/partitioning",
            "connector-development/connector-builder-ui/error-handling",
          ],
        },
      ],
    },
    {
      type: "category",
      label: "Low-code connector development",
      items: [
        {
          label: "Low-code CDK Intro",
          type: "doc",
          id: "connector-development/config-based/low-code-cdk-overview",
        },
        {
          type: "category",
          label: "Tutorial",
          items: [
            "connector-development/config-based/tutorial/getting-started",
            "connector-development/config-based/tutorial/create-source",
            "connector-development/config-based/tutorial/install-dependencies",
            "connector-development/config-based/tutorial/connecting-to-the-API-source",
            "connector-development/config-based/tutorial/reading-data",
            "connector-development/config-based/tutorial/incremental-reads",
            "connector-development/config-based/tutorial/testing",
          ],
        },
        {
          type: "category",
          label: "Understanding the YAML file",
          link: {
            type: "doc",
            id: "connector-development/config-based/understanding-the-yaml-file/yaml-overview",
          },
          items: [
            {
              type: `category`,
              label: `Requester`,
              link: {
                type: "doc",
                id: "connector-development/config-based/understanding-the-yaml-file/requester",
              },
              items: [
                "connector-development/config-based/understanding-the-yaml-file/request-options",
                "connector-development/config-based/understanding-the-yaml-file/authentication",
                "connector-development/config-based/understanding-the-yaml-file/error-handling",
              ],
            },
            "connector-development/config-based/understanding-the-yaml-file/incremental-syncs",
            "connector-development/config-based/understanding-the-yaml-file/pagination",
            "connector-development/config-based/understanding-the-yaml-file/partition-router",
            "connector-development/config-based/understanding-the-yaml-file/record-selector",
            "connector-development/config-based/understanding-the-yaml-file/reference",
          ],
        },
        "connector-development/config-based/advanced-topics",
      ],
    },

    {
      type: "category",
      label: "Connector Development Kit",
      link: {
        type: "doc",
        id: "connector-development/cdk-python/README",
      },
      items: [
        "connector-development/cdk-python/basic-concepts",
        "connector-development/cdk-python/schemas",
        "connector-development/cdk-python/full-refresh-stream",
        "connector-development/cdk-python/incremental-stream",
        "connector-development/cdk-python/http-streams",
        "connector-development/cdk-python/python-concepts",
        "connector-development/cdk-python/stream-slices",
      ],
    },
    {
      type: "category",
      label: "Testing Connectors",
      link: {
        type: "doc",
        id: "connector-development/testing-connectors/README",
      },
      items: [
        "connector-development/testing-connectors/connector-acceptance-tests-reference",
      ],
    },
    {
      type: "category",
      label: "Tutorials",
      items: [
        "connector-development/tutorials/cdk-speedrun",
        {
          type: "category",
          label: "Python CDK: Creating a HTTP API Source",
          items: [
            "connector-development/tutorials/cdk-tutorial-python-http/getting-started",
            "connector-development/tutorials/cdk-tutorial-python-http/creating-the-source",
            "connector-development/tutorials/cdk-tutorial-python-http/install-dependencies",
            "connector-development/tutorials/cdk-tutorial-python-http/define-inputs",
            "connector-development/tutorials/cdk-tutorial-python-http/connection-checking",
            "connector-development/tutorials/cdk-tutorial-python-http/declare-schema",
            "connector-development/tutorials/cdk-tutorial-python-http/read-data",
            "connector-development/tutorials/cdk-tutorial-python-http/use-connector-in-airbyte",
            "connector-development/tutorials/cdk-tutorial-python-http/test-your-connector",
          ],
        },
        "connector-development/tutorials/building-a-python-source",
        "connector-development/tutorials/building-a-java-destination",
        "connector-development/tutorials/profile-java-connector-memory",
      ],
    },
    "connector-development/connector-specification-reference",
    "connector-development/schema-reference",
    "connector-development/connector-metadata-file",
    "connector-development/best-practices",
    "connector-development/ux-handbook",
  ],
};

const connectorCatalog = {
  type: "category",
  label: "Connector Catalog",
  link: {
    type: "doc",
    id: "integrations/README",
  },
  items: [
    {
      type: "category",
      label: "Sources",
      link: {
        type: "generated-index",
      },
      items: [sourcePostgres, sourceMysql, ...getSourceConnectors()].sort((itemA, itemB) => itemA.label.localeCompare(itemB.label)),
    },
    {
      type: "category",
      label: "Destinations",
      link: {
        type: "generated-index",
      },
      items: getDestinationConnectors(),
    },
    {
      type: "doc",
      id: "integrations/custom-connectors",
    },
  ],
};

const contributeToAirbyte = {
  type: "category",
  label: "Contribute to Airbyte",
  link: {
    type: "doc",
    id: "contributing-to-airbyte/README",
  },
  items: [
    "contributing-to-airbyte/issues-and-requests",
    "contributing-to-airbyte/change-cdk-connector",
    "contributing-to-airbyte/submit-new-connector",
    "contributing-to-airbyte/writing-docs",
    {
      type: "category",
      label: "Resources",
      items: [
        "contributing-to-airbyte/resources/pull-requests-handbook",
        "contributing-to-airbyte/resources/code-style",
        "contributing-to-airbyte/resources/code-formatting",
        "contributing-to-airbyte/resources/developing-locally",
        "contributing-to-airbyte/resources/developing-on-docker",
      ],
    },
  ],
};

const deployAirbyte = {
  type: "category",
  label: "Deploy Airbyte",
  link: {
    type: "generated-index",
  },
  items: [
    {
      type: "doc",
      label: "On your local machine",
      id: "deploying-airbyte/local-deployment",
    },
    {
      type: "doc",
      label: "On AWS EC2",
      id: "deploying-airbyte/on-aws-ec2",
    },
    {
      type: "doc",
      label: "On AWS ECS",
      id: "deploying-airbyte/on-aws-ecs",
    },
    {
      type: "doc",
      label: "On Azure",
      id: "deploying-airbyte/on-azure-vm-cloud-shell",
    },
    {
      type: "doc",
      label: "On Google (GCP)",
      id: "deploying-airbyte/on-gcp-compute-engine",
    },
    {
      type: "doc",
      label: "On Kubernetes using Helm",
      id: "deploying-airbyte/on-kubernetes-via-helm",
    },
    {
      type: "doc",
      label: "On Restack",
      id: "deploying-airbyte/on-restack",
    },
    {
      type: "doc",
      label: "On Plural",
      id: "deploying-airbyte/on-plural",
    },
    {
      type: "doc",
      label: "On Oracle Cloud",
      id: "deploying-airbyte/on-oci-vm",
    },
    {
      type: "doc",
      label: "On DigitalOcean",
      id: "deploying-airbyte/on-digitalocean-droplet",
    },
  ],
};

const understandingAirbyte = {
  type: "category",
  label: "Understand Airbyte",
  items: [
    "understanding-airbyte/beginners-guide-to-catalog",
    "understanding-airbyte/airbyte-protocol",
    "understanding-airbyte/airbyte-protocol-docker",
    "understanding-airbyte/operations",
    "understanding-airbyte/high-level-view",
    "understanding-airbyte/jobs",
    "understanding-airbyte/tech-stack",
    "understanding-airbyte/cdc",
    "understanding-airbyte/supported-data-types",
    "understanding-airbyte/json-avro-conversion",
    "understanding-airbyte/database-data-catalog",
    "understanding-airbyte/schemaless-sources-and-destinations",
  ],
};

module.exports = {
  docs: [
    sectionHeader("Airbyte Connectors"),
    connectorCatalog,
    buildAConnector,
    "integrations/connector-support-levels",
    sectionHeader("Using Airbyte"),
    {
      type: "category",
      label: "Getting Started",
      link: {
        type: "doc",
        id: "using-airbyte/getting-started/readme",
      },
      items: [
        "using-airbyte/core-concepts/readme",
        "using-airbyte/getting-started/add-a-source",
        "using-airbyte/getting-started/add-a-destination",
        "using-airbyte/getting-started/set-up-a-connection",
      ],
    },
    {
      type: "category",
      label: "Configuring Connections",
      link: {
        type: "doc",
        id: "cloud/managing-airbyte-cloud/configuring-connections"
      },
      items: [
        "using-airbyte/core-concepts/sync-schedules",
        "using-airbyte/core-concepts/namespaces",
        {
          type: "category",
          label: "Sync Modes",
          link: {
            type: "doc",
            id: "using-airbyte/core-concepts/sync-modes/README"
          },
          items: [
            "using-airbyte/core-concepts/sync-modes/incremental-append-deduped",
            "using-airbyte/core-concepts/sync-modes/incremental-append",
            "using-airbyte/core-concepts/sync-modes/full-refresh-append",
            "using-airbyte/core-concepts/sync-modes/full-refresh-overwrite",
          ],
        },
        "using-airbyte/core-concepts/typing-deduping",
        "using-airbyte/core-concepts/basic-normalization",
        "cloud/managing-airbyte-cloud/manage-schema-changes",
        "cloud/managing-airbyte-cloud/manage-data-residency",
        "cloud/managing-airbyte-cloud/manage-connection-state",
        {
          type: "category",
          label: "Transformations",
          items: [
            "cloud/managing-airbyte-cloud/dbt-cloud-integration",
            "operator-guides/transformation-and-normalization/transformations-with-sql",
            "operator-guides/transformation-and-normalization/transformations-with-dbt",
            "operator-guides/transformation-and-normalization/transformations-with-airbyte",
          ]
        },
      ]
    },
    {
      type: "category",
      label: "Managing Syncs",
      items: [
        "cloud/managing-airbyte-cloud/review-connection-status",
        "cloud/managing-airbyte-cloud/review-sync-history",
        "operator-guides/browsing-output-logs",
        "operator-guides/reset",
      ],
    },
    {
      type: "category",
      label: "Workspace Management",
      items: [
        "using-airbyte/workspaces",
        "cloud/managing-airbyte-cloud/manage-airbyte-cloud-notifications",
        "cloud/managing-airbyte-cloud/manage-credits",
        "operator-guides/using-custom-connectors",
      ]
    },
    sectionHeader("Managing Airbyte"),
    deployAirbyte,
    {
      type: "category",
      label: "Self-Managed Enterprise",
      link: {
        type: "doc",
        id: "enterprise-setup/README",
      },
      items: [
        "enterprise-setup/implementation-guide",
        "enterprise-setup/upgrading-from-community",
      ]
    },
    "operator-guides/upgrading-airbyte",
    {
      type: "category",
      label: "Configuring Airbyte",
      link: {
        type: "doc",
        id: "operator-guides/configuring-airbyte",
      },
      items: [
        "operator-guides/configuring-airbyte-db",
        "operator-guides/configuring-connector-resources",
      ]
    },
    {
      type: "category",
      label: "Access Management",
      items: [
        {
          type: "category",
          label: "Single Sign-On (SSO)",
          link: {
            type: "doc",
            id: "access-management/sso"
          },
          items: [
            { type: "autogenerated", dirName: "access-management/sso-providers" },
          ]
        },
      ]
    },
    {
      type: "category",
      label: "Airbyte at Scale",
      items: [
        "operator-guides/collecting-metrics",
        "operator-guides/scaling-airbyte",
        "cloud/managing-airbyte-cloud/understand-airbyte-cloud-limits",
      ]
    },
    "operating-airbyte/security",
    {
      type: "category",
      label: "Integrating with Airbyte",
      items: [
        "operator-guides/using-the-airflow-airbyte-operator",
        "operator-guides/using-prefect-task",
        "operator-guides/using-dagster-integration",
        "operator-guides/using-kestra-plugin",
      ],
    },
    sectionHeader("Developer Guides"),
    {
      type: "doc",
      id: "api-documentation",
    },
    {
      type: "doc",
      id: "terraform-documentation",
    },
    {
      type: "doc",
      id: "cli-documentation",
    },
    understandingAirbyte,
    contributeToAirbyte,
    {
      type: "category",
      label: "Licenses",
      link: {
        type: "doc",
        id: "developer-guides/licenses/README",
      },
      items: [
        "developer-guides/licenses/license-faq",
        "developer-guides/licenses/elv2-license",
        "developer-guides/licenses/mit-license",
        "developer-guides/licenses/examples",
      ],
    },
    sectionHeader("Community"),
    "community/getting-support",
    "community/code-of-conduct",
    sectionHeader("Product Updates"),
    {
      type: "link",
      label: "Roadmap",
      href: "https://go.airbyte.com/roadmap",
    },
    {
      type: "category",
      label: "Release Notes",
      link: {
        type: "generated-index",
      },
      items: [
        "release_notes/november_2023",
        "release_notes/october_2023",
        "release_notes/upgrading_to_destinations_v2",
        "release_notes/september_2023",
        "release_notes/july_2023",
        "release_notes/june_2023",
        "release_notes/may_2023",
        "release_notes/april_2023",
        "release_notes/march_2023",
        "release_notes/february_2023",
        "release_notes/january_2023",
        "release_notes/december_2022",
        "release_notes/november_2022",
        "release_notes/october_2022",
        "release_notes/september_2022",
        "release_notes/august_2022",
        "release_notes/july_2022",
      ],
    },
  ],
};
