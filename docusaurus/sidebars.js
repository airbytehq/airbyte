const fs = require("fs");
const path = require("path");
const {
  parseMarkdownContentTitle,
  parseMarkdownFile,
} = require("@docusaurus/utils");
const matter = require("gray-matter");

const connectorsDocsRoot = "../docs/integrations";
const sourcesDocs = `${connectorsDocsRoot}/sources`;
const destinationDocs = `${connectorsDocsRoot}/destinations`;
const enterpriseConnectorDocs = `${connectorsDocsRoot}/enterprise-connectors`;

function getFilenamesInDir(prefix, dir, excludes) {
  return fs
    .readdirSync(dir)
    .filter(
      (fileName) =>
        !(
          fileName.endsWith(".inapp.md") ||
          fileName.endsWith("-migrations.md") ||
          fileName.endsWith(".js") ||
          fileName === "low-code.md"
        )
    )
    .map((fileName) => fileName.replace(".md", ""))
    .filter((fileName) => excludes.indexOf(fileName.toLowerCase()) === -1)
    .map((filename) => {
      // Get the first header of the markdown document
      try {
        const filePath = path.join(dir, `${filename}.md`);
        const fileContent = fs.readFileSync(filePath, 'utf8');
        const firstLine = fileContent.split('\n').find(line => line.trim().startsWith('# '));
        const contentTitle = firstLine ? firstLine.replace(/^#\s*/, '').trim() : filename;
        return {
          type: 'doc',
          id: prefix + filename,
          label: contentTitle || filename
        };
      } catch (error) {
        console.warn(`Warning: Using filename as title for ${path.join(prefix, filename)}`);
        return {
          type: 'doc',
          id: prefix + filename,
          label: filename
        };
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

      return {
        type: "doc",
        id: path.join(prefix, filename),
        label: contentTitle,
      };
    });
}

function getSourceConnectors() {
  return getFilenamesInDir("integrations/sources/", sourcesDocs, [
    "readme",
    "postgres",
    "mongodb-v2",
    "mssql",
    "mysql",
  ]);
}

function getDestinationConnectors() {
  return getFilenamesInDir("integrations/destinations/", destinationDocs, [
    "readme",
    "s3",
    "postgres",
  ]);
}

function getEnterpriseConnectors() {
  return getFilenamesInDir(
    "integrations/enterprise-connectors/",
    enterpriseConnectorDocs, ["readme"]
  );
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

const sourceMongoDB = {
  type: "category",
  label: "Mongo DB",
  link: {
    type: "doc",
    id: "integrations/sources/mongodb-v2",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "integrations/sources/mongodb-v2-migrations",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "integrations/sources/mongodb-v2/mongodb-v2-troubleshooting",
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

const sourceMssql = {
  type: "category",
  label: "MS SQL Server (MSSQL)",
  link: {
    type: "doc",
    id: "integrations/sources/mssql",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "integrations/sources/mssql/mssql-troubleshooting",
    },
  ],
};

const destinationS3 = {
  type: "category",
  label: "S3",
  link: {
    type: "doc",
    id: "integrations/destinations/s3",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "integrations/destinations/s3-migrations",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "integrations/destinations/s3/s3-troubleshooting",
    },
  ],
};

const destinationPostgres = {
  type: "category",
  label: "Postgres",
  link: {
    type: "doc",
    id: "integrations/destinations/postgres",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "integrations/destinations/postgres/postgres-troubleshooting",
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
  label: "Building Connectors",
  link: {
    type: "doc",
    id: "connector-development/README",
  },
  items: [
    {
      type: "category",
      label: "No-Code Connector Builder",
      items: [
        "connector-development/connector-builder-ui/overview",
        "connector-development/connector-builder-ui/connector-builder-compatibility",
        "connector-development/connector-builder-ui/tutorial",
        "connector-development/connector-builder-ui/ai-assist",
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
      label: "Low-Code CDK",
      items: [
        {
          label: "Low-Code CDK Intro",
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
      label: "Python CDK",
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
        {
          type: "category",
          label: "Tutorials",
          items: [
            "connector-development/tutorials/cdk-speedrun",
            {
              type: "category",
              label: "Python CDK: Creating a Python Source",
              items: [
                "connector-development/tutorials/custom-python-connector/getting-started",
                "connector-development/tutorials/custom-python-connector/environment-setup",
                "connector-development/tutorials/custom-python-connector/reading-a-page",
                "connector-development/tutorials/custom-python-connector/reading-multiple-pages",
                "connector-development/tutorials/custom-python-connector/check-and-error-handling",
                "connector-development/tutorials/custom-python-connector/discover",
                "connector-development/tutorials/custom-python-connector/incremental-reads",
                "connector-development/tutorials/custom-python-connector/reading-from-a-subresource",
                "connector-development/tutorials/custom-python-connector/concurrency",
              ],
            },
          ],
        },
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
    "connector-development/connector-specification-reference",
    "connector-development/writing-connector-docs",
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
        type: "doc",
        id: "integrations/sources/README",
      },
      items: [
        sourcePostgres,
        sourceMongoDB,
        sourceMysql,
        sourceMssql,
        ...getSourceConnectors(),
      ].sort((itemA, itemB) => {
        const labelA = itemA?.label || '';
        const labelB = itemB?.label || '';
        return labelA.localeCompare(labelB);
      }),
    },
    {
      type: "category",
      label: "Destinations",
      link: {
        type: "doc",
        id: "integrations/destinations/README",
      },
      items: [
        destinationS3,
        destinationPostgres,
        ...getDestinationConnectors(),
      ].sort((itemA, itemB) => {
        const labelA = itemA?.label || '';
        const labelB = itemB?.label || '';
        return labelA.localeCompare(labelB);
      }),
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
    "contributing-to-airbyte/developing-locally",
    "contributing-to-airbyte/writing-docs",
    {
      type: "category",
      label: "Resources",
      items: [
        "contributing-to-airbyte/resources/pull-requests-handbook",
        "contributing-to-airbyte/resources/qa-checks",
      ],
    },
  ],
};

const deployAirbyte = {
  type: "category",
  label: "Deploy Airbyte",
  link: {
    type: "doc",
    id: "deploying-airbyte/deploying-airbyte",
  },
  items: [
    {
      type: "category",
      label: "Infrastructure",
      items: [
        "deploying-airbyte/infrastructure/aws",
        "deploying-airbyte/infrastructure/gcp",
        // "deploying-airbyte/infrastructure/azure",
      ],
    },

    {
      type: "category",
      label: "Integrations",
      items: [
        "deploying-airbyte/integrations/authentication",
        "deploying-airbyte/integrations/storage",
        "deploying-airbyte/integrations/secrets",
        "deploying-airbyte/integrations/database",
        // "deploying-airbyte/integrations/monitoring",
        "deploying-airbyte/integrations/ingress",
        "deploying-airbyte/integrations/custom-image-registries",
      ],
    },

    {
      type: "doc",
      label: "Creating a Secret",
      id: "deploying-airbyte/creating-secrets",
    },
    {
      type: "doc",
      id: "deploying-airbyte/troubleshoot-deploy",
    },
    {
      type: "doc",
      id: "deploying-airbyte/migrating-from-docker-compose",
    },
    {
      type: "doc",
      id: "deploying-airbyte/abctl-ec2",
    },
  ],
};

const connectionConfigurations = {
  type: "category",
  label: "Data Transfer Options",
  link: {
    type: "doc",
    id: "cloud/managing-airbyte-cloud/configuring-connections",
  },
  items: [
    "using-airbyte/core-concepts/sync-schedules",
    "using-airbyte/core-concepts/namespaces",
    "using-airbyte/configuring-schema",
    "using-airbyte/schema-change-management",
    {
      type: "category",
      label: "Sync Modes",
      link: {
        type: "doc",
        id: "using-airbyte/core-concepts/sync-modes/README",
      },
      items: [
        "using-airbyte/core-concepts/sync-modes/incremental-append-deduped",
        "using-airbyte/core-concepts/sync-modes/incremental-append",
        "using-airbyte/core-concepts/sync-modes/full-refresh-append",
        "using-airbyte/core-concepts/sync-modes/full-refresh-overwrite",
        "using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped",
      ],
    },
  ],
};

const understandingAirbyte = {
  type: "category",
  label: "Understand Airbyte",
  items: [
    "understanding-airbyte/high-level-view",
    "understanding-airbyte/airbyte-protocol",
    "understanding-airbyte/airbyte-protocol-docker",
    "understanding-airbyte/jobs",
    "understanding-airbyte/database-data-catalog",
    "understanding-airbyte/beginners-guide-to-catalog",
    "understanding-airbyte/supported-data-types",
    "understanding-airbyte/secrets",
    "understanding-airbyte/cdc",
    "understanding-airbyte/resumability",
    "understanding-airbyte/json-avro-conversion",
    "understanding-airbyte/schemaless-sources-and-destinations",
    "understanding-airbyte/tech-stack",
  ],
};

module.exports = {
  docs: [
    sectionHeader("Getting Started"),
    {
      type: "doc",
      id: "using-airbyte/getting-started/readme",
    },
    {
      type: "doc",
      label: "Quickstart",
      id: "using-airbyte/getting-started/oss-quickstart",
    },
    {
      type: "doc",
      id: "using-airbyte/core-concepts/readme",
    },
    {
      type: "category",
      label: "Moving Data",
      items: [
        "using-airbyte/getting-started/add-a-source",
        "using-airbyte/getting-started/add-a-destination",
        "using-airbyte/getting-started/set-up-a-connection",
      ],
    },
    sectionHeader("Airbyte Connectors"),
    connectorCatalog,
    buildAConnector,
    "integrations/connector-support-levels",
    sectionHeader("Using Airbyte"),
    connectionConfigurations,
    {
      type: "doc",
      id: "using-airbyte/core-concepts/typing-deduping",
    },
    {
      type: "doc",
      id: "using-airbyte/mappings",
    },
    {
      type: "category",
      label: "Transformations",
      items: ["cloud/managing-airbyte-cloud/dbt-cloud-integration"],
    },
    {
      type: "category",
      label: "Managing Syncs",
      items: [
        "cloud/managing-airbyte-cloud/review-connection-status",
        "cloud/managing-airbyte-cloud/review-connection-timeline",
        "operator-guides/refreshes",
        "operator-guides/clear",
        "operator-guides/browsing-output-logs",
        "cloud/managing-airbyte-cloud/manage-connection-state",
      ],
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
        "enterprise-setup/api-access-config",
        "enterprise-setup/scaling-airbyte",
        "enterprise-setup/upgrading-from-community",
        {
          type: "category",
          label: "Enterprise Connectors",
          link: {
            type: "doc",
            id: "integrations/enterprise-connectors/README",
          },
          items: [...getEnterpriseConnectors()].sort((itemA, itemB) => {
            const labelA = itemA?.label || '';
            const labelB = itemB?.label || '';
            return labelA.localeCompare(labelB);
          }),
        },
      ],
    },
    {
      type: "category",
      label: "Upgrading Airbyte",
      link: {
        type: "doc",
        id: "operator-guides/upgrading-airbyte",
      },
      items: ["managing-airbyte/connector-updates"],
    },
    {
      type: "category",
      label: "Configuring Airbyte",
      link: {
        type: "doc",
        id: "operator-guides/configuring-airbyte",
      },
      items: [
        "operator-guides/configuring-connector-resources",
        "operator-guides/telemetry",
      ],
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
            id: "access-management/sso",
          },
          items: [
            {
              type: "autogenerated",
              dirName: "access-management/sso-providers",
            },
          ],
        },
        {
          type: "category",
          label: "Role-Based Access Control (RBAC)",
          link: {
            type: "doc",
            id: "access-management/rbac",
          },
          items: [
            { 
              type: "doc", 
              id: "access-management/role-mapping" 
            },
          ],
        },
      ],
    },
    {
      type: "category",
      label: "Airbyte at Scale",
      items: [
        "operator-guides/collecting-metrics",
        "operator-guides/scaling-airbyte",
        "cloud/managing-airbyte-cloud/understand-airbyte-cloud-limits",
      ],
    },
    "operating-airbyte/security",
    {
      type: "category",
      label: "Integrating with Airbyte",
      items: [
        "using-airbyte/configuring-api-access",
        "operator-guides/using-the-airflow-airbyte-operator",
        "operator-guides/using-prefect-task",
        "operator-guides/using-dagster-integration",
        "operator-guides/using-kestra-plugin",
        "operator-guides/using-orchestra-task",
      ],
    },
    {
      type: "category",
      label: "Account Management",
      items: [
        "cloud/managing-airbyte-cloud/manage-data-residency",
        "using-airbyte/workspaces",
        "cloud/managing-airbyte-cloud/manage-airbyte-cloud-notifications",
        "cloud/managing-airbyte-cloud/manage-credits",
        "operator-guides/using-custom-connectors",
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
      label: "Using PyAirbyte",
      id: "using-airbyte/pyairbyte/getting-started",
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
        description: "We release new self-managed versions of Airbyte regularly. Airbyte Cloud customers always have the latest enhancements.",
      },
      items: [
        "release_notes/v-1.4",
        "release_notes/v-1.3",
        "release_notes/v-1.2",
        "release_notes/v-1.1",
        "release_notes/v-1.0",
        "release_notes/aug_2024",
        "release_notes/july_2024",
        "release_notes/june_2024",
        "release_notes/may_2024",
        "release_notes/april_2024",
        "release_notes/march_2024",
        "release_notes/february_2024",
        "release_notes/january_2024",
        "release_notes/december_2023",
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

// Any temporarily archived content should be added here with a comment
// to indicate when it was archived and why.
// You can still view docs that are not linked to in the sidebar.

// Java Destination template is not currently available for use
// "connector-development/tutorials/building-a-java-destination",
