const sectionHeader = (title) => ({
  type: "html",
  value: title,
  className: "navbar__category",
});

const buildAConnector = {
  type: "category",
  label: "Build connectors",
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
            "connector-development/connector-builder-ui/global-configuration",
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
    "connector-development/submit-new-connector",
    "connector-development/connector-breaking-changes",
    "connector-development/connector-specification-reference",
    "connector-development/partner-certified-destinations",
    "operator-guides/using-custom-connectors",
    "connector-development/debugging-docker",
    "connector-development/writing-connector-docs",
    "connector-development/schema-reference",
    "connector-development/connector-metadata-file",
    "connector-development/best-practices",
    "connector-development/ux-handbook",
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
        "deploying-airbyte/integrations/ingress-1-7",
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
      id: "deploying-airbyte/migrating-from-docker-compose",
    },
    {
      type: "doc",
      id: "deploying-airbyte/abctl-ec2",
    },
    "deploying-airbyte/chart-v2-community",
    "deploying-airbyte/values",
    {
      type: "category",
      label: "abctl",
      link: {
        type: "doc",
        id: "deploying-airbyte/abctl/index",
      },
      items: [
        {
          type: "doc",
          id: "deploying-airbyte/troubleshoot-deploy",
        },
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
        sectionHeader("Get started"),

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
        sectionHeader("Move and manage data"),
        {
          type: "category",
          label: "Move data",
          link: {
            type: "doc",
            id: "move-data/readme",
          },
          items: [
            {
              type: "category",
              label: "Sources, destinations, and connectors",
              link: {
                type: "doc",
                id: "move-data/sources-destinations-connectors",
              },
              items: [
                "using-airbyte/getting-started/add-a-source",
                "using-airbyte/getting-started/add-a-destination",
                "using-airbyte/oauth",
                "using-airbyte/delivery-methods",
              ],
            },
            {
              type: "category",
              label: "Connections and streams",
              link: {
                type: "doc",
                id: "using-airbyte/getting-started/set-up-a-connection",
              },
              items: [
                "move-data/add-connection",
                {
                  type: "category",
                  label: "Manage connections",
                  link: {
                    type: "doc",
                    id: "cloud/managing-airbyte-cloud/configuring-connections",
                  },
                  items: [
                    "cloud/managing-airbyte-cloud/review-connection-status",
                    "cloud/managing-airbyte-cloud/review-connection-timeline",
                    "using-airbyte/configuring-schema",
                    "using-airbyte/mappings",
                    "cloud/managing-airbyte-cloud/dbt-cloud-integration",
                    "operator-guides/refreshes",
                    "operator-guides/clear",
                    "operator-guides/browsing-output-logs",
                    "cloud/managing-airbyte-cloud/manage-connection-state",
                    "using-airbyte/core-concepts/sync-schedules",
                    "using-airbyte/core-concepts/namespaces",
                    "using-airbyte/schema-change-management",
                    "using-airbyte/tagging",
                    "using-airbyte/core-concepts/typing-deduping",
                    "using-airbyte/core-concepts/direct-load-tables",
                    "understanding-airbyte/airbyte-metadata-fields",
                  ],
                },
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
                    {
                      type: "category",
                      label: "Change Data Capture (CDC)",
                      link: {
                        type: "generated-index",
                        title: "Change Data Capture (CDC)",
                        description: "Learn about CDC in Airbyte and best practices for configuration.",
                      },
                      items: [
                        "understanding-airbyte/cdc",
                        "understanding-airbyte/cdc-best-practices",
                      ],
                    },
                  ],
                },
              ],
            },
            {
              type: "category",
              label: "Data activation (reverse ETL)",
              link: {
                type: "doc",
                id: "move-data/elt-data-activation",
              },
              items: [
                "move-data/rejected-records"
              ],
            },
            "using-airbyte/sync-files-and-records",
          ],
        },
        {
          type: "category",
          label: "Organizations and workspaces",
          link: {
            type: "doc",
            id: "organizations-workspaces/readme",
          },
          items: [
            {
              type: "category",
              label: "Organizations",
              link: {
                type: "doc",
                id: "organizations-workspaces/organizations/readme",
              },
              items: [
                "organizations-workspaces/organizations/switch-organizations",
                "cloud/managing-airbyte-cloud/manage-credits",
                "cloud/managing-airbyte-cloud/manage-data-workers",
              ],
            },
            {
              type: "category",
              label: "Workspaces",
              link: {
                type: "doc",
                id: "organizations-workspaces/workspaces/readme",
              },
              items: [
                "using-airbyte/workspaces",
                "cloud/managing-airbyte-cloud/manage-data-residency",
                "cloud/managing-airbyte-cloud/manage-airbyte-cloud-notifications",
              ],
            },
            {
              type: "category",
              label: "Access management",
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
          ],
        },   
        buildAConnector,     
        sectionHeader("Deploy and upgrade Airbyte"),
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
            "enterprise-setup/multi-region",
            "enterprise-setup/audit-logging",
            "enterprise-setup/scaling-airbyte",
            "enterprise-setup/upgrade-service-account",
            "enterprise-setup/upgrading-from-community",
            "enterprise-setup/chart-v2-enterprise",
          ],
        },
        {
          type: "category",
          label: "Enterprise Flex",
          link: {
            type: "doc",
            id: "enterprise-flex/readme",
          },
          items: [
            "enterprise-flex/getting-started",
            "enterprise-flex/data-plane",
            "enterprise-flex/data-plane-util",
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
          label: "Airbyte at Scale",
          items: [
            {
              type: "category",
              label: "Collecting Metrics",
              link: {
                type: "doc",
                id: "operator-guides/collecting-metrics",
              },
              items: [
                {
                  type: "doc",
                  id: "operator-guides/open-telemetry",
                },
              ],
            },
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
            "operator-guides/using-the-airflow-airbyte-operator",
            "operator-guides/using-prefect-task",
            "operator-guides/using-dagster-integration",
            "operator-guides/using-kestra-plugin",
            "operator-guides/using-orchestra-task",
          ],
        },
        sectionHeader("Advanced"),
        "using-airbyte/configuring-api-access",
        understandingAirbyte,
      ],
    },
  ],
};
