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
      label: "Connector Builder",
      link: {
        type: "doc",
        id: "connector-development/connector-builder-ui/overview",
      },
      items: [
        "connector-development/connector-builder-ui/tutorial",
        "connector-development/connector-builder-ui/ai-assist",
        "connector-development/connector-builder-ui/custom-components",
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
            "connector-development/connector-builder-ui/async-streams",
            "connector-development/connector-builder-ui/stream-templates",
          ],
        },
        {
          label: "Low-Code CDK Intro",
          type: "doc",
          id: "connector-development/config-based/low-code-cdk-overview",
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
            "connector-development/config-based/understanding-the-yaml-file/property-chunking",
            "connector-development/config-based/understanding-the-yaml-file/rate-limit-api-budget",
            "connector-development/config-based/understanding-the-yaml-file/record-selector",
            "connector-development/config-based/understanding-the-yaml-file/file-syncing",
            "connector-development/config-based/understanding-the-yaml-file/reference",
          ],
        },
        {
          type: "category",
          label: "Advanced Topics",
          items: [
            "connector-development/config-based/advanced-topics/component-schema-reference",
            "connector-development/config-based/advanced-topics/custom-components",
            "connector-development/config-based/advanced-topics/oauth",
            "connector-development/config-based/advanced-topics/how-framework-works",
            "connector-development/config-based/advanced-topics/object-instantiation",
            "connector-development/config-based/advanced-topics/parameters",
            "connector-development/config-based/advanced-topics/references",
            "connector-development/config-based/advanced-topics/string-interpolation",
          ],
        },
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
        "connector-development/cdk-python/resumable-full-refresh-stream",
        "connector-development/cdk-python/incremental-stream",
        "connector-development/cdk-python/http-streams",
        "connector-development/cdk-python/stream-slices",
        "connector-development/cdk-python/migration-to-base-image",
        {
          type: "category",
          label: "Tutorial: Creating a connector with Python CDK",
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
    "connector-development/local-connector-development",
    "connector-development/connector-specification-reference",
    "connector-development/partner-certified-destinations",
    "connector-development/debugging-docker",
    "connector-development/writing-connector-docs",
    "connector-development/schema-reference",
    "connector-development/connector-metadata-file",
    "connector-development/best-practices",
    "connector-development/ux-handbook",
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
    "understanding-airbyte/airbyte-protocol-versioning",
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
    "understanding-airbyte/heartbeats",
  ],
};

module.exports = {
  platform: [
    {
      type: "category",
      collapsible: false,
      label: "Airbyte Platform",
      link: {
        type: "doc",
        id: "readme",
      },
      items: [
        sectionHeader("Getting Started"),

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
          type: "doc",
          id: "using-airbyte/getting-started/academy",
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
        {
          type: "link",
          label: "Connector Catalog",
          href: "/integrations/",
        },
        buildAConnector,
        {
          type: "doc",
          id: "using-airbyte/oauth",
        },
        sectionHeader("Using Airbyte"),
        connectionConfigurations,
        {
          type: "doc",
          id: "using-airbyte/core-concepts/direct-load-tables",
        },
        {
          type: "doc",
          id: "using-airbyte/core-concepts/typing-deduping",
        },
        {
          type: "doc",
          id: "using-airbyte/sync-files-and-records",
        },
        {
          type: "doc",
          id: "using-airbyte/delivery-methods",
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
        {
          type: "doc",
          id: "using-airbyte/tagging",
        },
        {
          type: "doc",
          id: "understanding-airbyte/airbyte-metadata-fields",
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
            "enterprise-setup/multi-region",
            "enterprise-setup/audit-logging",
            "enterprise-setup/scaling-airbyte",
            "enterprise-setup/upgrade-service-account",
            "enterprise-setup/upgrading-from-community",
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
                  id: "access-management/role-mapping",
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
        {
          type: "category",
          label: "Security",
          link: {
            type: "doc",
            id: "operating-airbyte/security",
          },
          items: [
            {
              type: "doc",
              id: "operating-airbyte/ip-allowlist",
            },
          ],
        },
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
        contributeToAirbyte,
        "community/getting-support",
        "community/code-of-conduct",
        sectionHeader("Product Updates"),
        {
          type: "link",
          label: "Roadmap",
          href: "https://go.airbyte.com/roadmap",
        },
      ],
    },
  ],
};
