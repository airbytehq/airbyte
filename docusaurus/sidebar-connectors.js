const fs = require("fs");
const path = require("path");
const {
  REGISTRY_CACHE_PATH,
  SOURCES_DOCS,
  DESTINATIONS_DOCS,
  ENTERPRISE_CONNECTORS_DOCS,
} = require("./src/scripts/constants");

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
          key: `${prefix}${filename}-category`,
          link: { type: "doc", id: path.join(prefix, filename) },
          items: [
            {
              type: "doc",
              id: path.join(prefix, `${filename}-migrations`),
              label: "Migration Guide",
              key: `${prefix}${filename}-migrations`,
            },
          ],
        };
      }

      return {
        type: "doc",
        id: prefix + filename,
        label: contentTitle,
        key: `${prefix}${filename}`,
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

function groupConnectorsBySupportLevel(connectors, keyPrefix = "") {
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
      key: `${keyPrefix}airbyte`,
      items: grouped.certified.sort((a, b) => a.label.localeCompare(b.label)),
    });
  }

  if (grouped.community.length > 0) {
    categories.push({
      type: "category",
      label: "Marketplace",
      collapsible: true,
      collapsed: true,
      key: `${keyPrefix}marketplace`,
      items: grouped.community.sort((a, b) => a.label.localeCompare(b.label)),
    });
  }

  if (grouped.enterprise.length > 0) {
    categories.push({
      type: "category",
      label: "Enterprise",
      collapsible: true,
      collapsed: true,
      key: `${keyPrefix}enterprise`,
      items: grouped.enterprise.sort((a, b) => a.label.localeCompare(b.label)),
    });
  }

  return categories;
}

const sourcePostgres = {
  type: "category",
  label: "Postgres",
  key: "sources-postgres-category",
  link: {
    type: "doc",
    id: "sources/postgres",
  },
  items: [
    {
      type: "doc",
      label: "Cloud SQL for Postgres",
      id: "sources/postgres/cloud-sql-postgres",
      key: "sources-postgres-cloud-sql",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/postgres/postgres-troubleshooting",
      key: "sources-postgres-troubleshooting",
    },
  ],
};

const sourceMongoDB = {
  type: "category",
  label: "Mongo DB",
  key: "sources-mongodb-v2-category",
  link: {
    type: "doc",
    id: "sources/mongodb-v2",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "sources/mongodb-v2-migrations",
      key: "sources-mongodb-v2-migrations",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/mongodb-v2/mongodb-v2-troubleshooting",
      key: "sources-mongodb-v2-troubleshooting",
    },
  ],
};

const sourceMysql = {
  type: "category",
  label: "MySQL",
  key: "sources-mysql-category",
  link: {
    type: "doc",
    id: "sources/mysql",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/mysql/mysql-troubleshooting",
      key: "sources-mysql-troubleshooting",
    },
  ],
};

const sourceMssql = {
  type: "category",
  label: "MS SQL Server (MSSQL)",
  key: "sources-mssql-category",
  link: {
    type: "doc",
    id: "sources/mssql",
  },
  items: [
    {
      type: "doc",
      label: "Troubleshooting",
      id: "sources/mssql/mssql-troubleshooting",
      key: "sources-mssql-troubleshooting",
    },
  ],
};
function getSourceConnectors(registry) {
  const sources = getFilenamesInDir("sources/", SOURCES_DOCS, [
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
    ENTERPRISE_CONNECTORS_DOCS,
    ["readme"],
  );
  const enterpriseSourcesWithSupportLevel = enterpriseSources
  .filter((item) => {
    const itemId = item.id || item.link?.id;
    return itemId && itemId.includes("source");
  })
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
  key: "destinations-s3-category",
  link: {
    type: "doc",
    id: "destinations/s3",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "destinations/s3-migrations",
      key: "destinations-s3-migrations",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "destinations/s3/s3-troubleshooting",
      key: "destinations-s3-troubleshooting",
    },
  ],
};

const destinationPostgres = {
  type: "category",
  label: "Postgres",
  key: "destinations-postgres-category",
  link: {
    type: "doc",
    id: "destinations/postgres",
  },
  items: [
    {
      type: "doc",
      label: "Migration Guide",
      id: "destinations/postgres-migrations",
      key: "destinations-postgres-migrations",
    },
    {
      type: "doc",
      label: "Troubleshooting",
      id: "destinations/postgres/postgres-troubleshooting",
      key: "destinations-postgres-troubleshooting",
    },
  ],
};

// Mssql destination is on the connector registry as mssql-v2, so we need to manually create the sidebar item
const destinationMsSql = {
  type: "category",
  label: "MS SQL Server (MSSQL)",
  key: "destinations-mssql-category",
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
      key: "destinations-mssql-migrations",
    },
  ],
};

function getDestinationConnectors(registry) {
  const specialDestinationConnectors = [destinationS3, destinationPostgres];
  const destinations = getFilenamesInDir("destinations/", DESTINATIONS_DOCS, [
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
    ENTERPRISE_CONNECTORS_DOCS,
    ["readme"],
  );
  const enterpriseDestinationsWithSupportLevel = enterpriseDestinations
  .filter((item) => {
    const itemId = item.id || item.link?.id;
    return itemId && itemId.includes("destination");
  })
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
    "sources-",
  );
  const destinationsBySupportLevel = groupConnectorsBySupportLevel(
    destinationConnectors,
    "destinations-",
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
      "speed-improvements",
    ],
  };
}

const connectorSidebar = buildConnectorSidebar();

module.exports = {
  connectors: [connectorSidebar],
};
