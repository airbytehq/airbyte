const fs = require("fs");
const path = require("path");

const REGISTRY_CACHE_PATH = path.join(
  __dirname,
  "src",
  "data",
  "connector_registry_slim.json",
);

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
        ),
    )
    .map((fileName) => fileName.replace(".md", ""))
    .filter((fileName) => excludes.indexOf(fileName.toLowerCase()) === -1)
    .map((filename) => {
      let contentTitle = filename;

      // Get the first header of the markdown document
      try {
        const filePath = path.join(dir, `${filename}.md`);
        const fileContent = fs.readFileSync(filePath, "utf8");
        const firstLine = fileContent
          .split("\n")
          .find((line) => line.trim().startsWith("# "));
        contentTitle = firstLine
          ? firstLine.replace(/^#\s*/, "").trim()
          : filename;
      } catch (error) {
        console.warn(
          `Warning: Using filename as title for ${path.join(prefix, filename)}`,
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

      return {
        type: "doc",
        id: prefix + filename,
        label: contentTitle,
      };
    });
}

function loadConnectorRegistry() {
  try {
    if (fs.existsSync(REGISTRY_CACHE_PATH)) {
      const data = fs.readFileSync(REGISTRY_CACHE_PATH, "utf8");
      return JSON.parse(data);
    }
  } catch (error) {
    console.warn("Error loading connector registry data:", error.message);
  }
  return [];
}

function addSupportLevelToConnectors(connectors, registry) {
  return connectors.map((item) => {
    // Get the ID from either doc-type or category-type items
    const id = item.type === "doc" ? item.id : item.link && item.link.id;

    if (!id) {
      return item;
    }

    let connectorInfo = registry.find((record) => record.docUrl.includes(id));

    if (connectorInfo) {
      return {
        ...item,
        customProps: {
          ...item.customProps,
          supportLevel: connectorInfo.supportLevel,
        },
      };
    }

    return item;
  });
}

function groupConnectorsBySupportLevel(connectors) {
  const grouped = connectors.reduce(
    (acc, item) => {
      const supportLevel = item.customProps?.supportLevel || "community";
      if (acc[supportLevel]) {
        acc[supportLevel].push(item);
      } else {
        acc.community.push(item);
      }
      return acc;
    },
    { certified: [], community: [], enterprise: [] },
  );

  // Create categories for each support level
  const categories = [];

  if (grouped.certified.length > 0) {
    categories.push({
      type: "category",
      label: "Airbyte",
      collapsible: true,
      collapsed: true,
      items: grouped.certified.sort((a, b) => a.label.localeCompare(b.label)),
    });
  }

  if (grouped.community.length > 0) {
    categories.push({
      type: "category",
      label: "Marketplace",
      collapsible: true,
      collapsed: true,
      items: grouped.community.sort((a, b) => a.label.localeCompare(b.label)),
    });
  }

  if (grouped.enterprise.length > 0) {
    categories.push({
      type: "category",
      label: "Enterprise",
      collapsible: true,
      collapsed: true,
      items: grouped.enterprise.sort((a, b) => a.label.localeCompare(b.label)),
    });
  }

  return categories;
}

const sourcePostgres = {
  type: "category",
  label: "Postgres",
  link: {
    type: "doc",
    id: "sources/postgres",
  },
  items: [
    {
      type: "doc",
      label: "Cloud SQL for Postgres",
      id: "sources/postgres/cloud-sql-postgres",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/postgres/postgres-troubleshooting",
    },
  ],
};

const sourceMongoDB = {
  type: "category",
  label: "Mongo DB",
  link: {
    type: "doc",
    id: "sources/mongodb-v2",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "sources/mongodb-v2-migrations",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/mongodb-v2/mongodb-v2-troubleshooting",
    },
  ],
};

const sourceMysql = {
  type: "category",
  label: "MySQL",
  link: {
    type: "doc",
    id: "sources/mysql",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/mysql/mysql-troubleshooting",
    },
  ],
};

const sourceMssql = {
  type: "category",
  label: "MS SQL Server (MSSQL)",
  link: {
    type: "doc",
    id: "sources/mssql",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/mssql/mssql-troubleshooting",
    },
  ],
};
function getSourceConnectors(registry) {
  const sources = getFilenamesInDir("sources/", sourcesDocs, [
    "readme",
    "postgres",
    "mongodb-v2",
    "mssql",
    "mysql",
  ]);

  const specialSources = [
    sourcePostgres,
    sourceMongoDB,
    sourceMysql,
    sourceMssql,
  ];
  const enterpriseSources = getFilenamesInDir(
    "enterprise-connectors/",
    enterpriseConnectorDocs,
    ["readme"],
  );
  const enterpriseSourcesWithSupportLevel = enterpriseSources
    .filter((item) => item.id.includes("source"))
    .map((item) => {
      return {
        ...item,
        customProps: { ...item.customProps, supportLevel: "enterprise" },
      };
    });
  const sourcesWithSupportLevel = addSupportLevelToConnectors(
    [...specialSources, ...sources],
    registry,
  );

  return [...sourcesWithSupportLevel, ...enterpriseSourcesWithSupportLevel];
}

const destinationS3 = {
  type: "category",
  label: "S3",
  link: {
    type: "doc",
    id: "destinations/s3",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "destinations/s3-migrations",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "destinations/s3/s3-troubleshooting",
    },
  ],
};

const destinationPostgres = {
  type: "category",
  label: "Postgres",
  link: {
    type: "doc",
    id: "destinations/postgres",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "destinations/postgres/postgres-troubleshooting",
    },
  ],
};

// Mssql destination is on the connector registry as mssql-v2, so we need to manually create the sidebar item
const destinationMsSql = {
  type: "category",
  label: "MS SQL Server (MSSQL)",
  link: {
    type: "doc",
    id: "destinations/mssql",
  },
  customProps: {
    supportLevel: "certified",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "destinations/mssql-migrations",
    },
  ],
};

function getDestinationConnectors(registry) {
  const specialDestinationConnectors = [destinationS3, destinationPostgres];
  const destinations = getFilenamesInDir("destinations/", destinationDocs, [
    "s3",
    "postgres",
    "mssql",
    "readme",
  ]);
  const destinationsWithSupportLevel = addSupportLevelToConnectors(
    [...specialDestinationConnectors, ...destinations],
    registry,
  );

  const enterpriseDestinations = getFilenamesInDir(
    "enterprise-connectors/",
    enterpriseConnectorDocs,
    ["readme"],
  );
  const enterpriseDestinationsWithSupportLevel = enterpriseDestinations
    .filter((item) => item.id.includes("destination"))
    .map((item) => {
      return {
        ...item,
        customProps: {
          ...item.customProps,
          supportLevel: "enterprise",
        },
      };
    });

  return [
    ...destinationsWithSupportLevel,
    ...enterpriseDestinationsWithSupportLevel,
    destinationMsSql,
  ];
}

function buildConnectorSidebar() {
  const registry = loadConnectorRegistry();

  const sourcesWithSupportLevel = getSourceConnectors(registry);

  const destinationConnectors = getDestinationConnectors(registry);

  const sourcesBySupportLevel = groupConnectorsBySupportLevel(
    sourcesWithSupportLevel,
  );
  const destinationsBySupportLevel = groupConnectorsBySupportLevel(
    destinationConnectors,
  );

  return {
    type: "category",
    label: "Connectors",
    collapsible: false,
    link: {
      type: "doc",
      id: "README",
    },
    items: [
      {
        type: "category",
        label: "Sources",
        link: {
          type: "doc",
          id: "sources/README",
        },
        collapsible: true,
        collapsed: false,
        items: sourcesBySupportLevel,
      },
      {
        type: "category",
        label: "Destinations",
        link: {
          type: "doc",
          id: "destinations/README",
        },
        collapsible: true,
        collapsed: false,
        items: destinationsBySupportLevel,
      },
      "connector-support-levels",
      {
        type: "doc",
        id: "custom-connectors",
      },
      "locating-files-local-destination",
    ],
  };
}

const connectorSidebar = buildConnectorSidebar();

module.exports = {
  connectors: [connectorSidebar],
};
