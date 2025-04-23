const fs = require("fs");
const path = require("path");
const {
  parseMarkdownContentTitle,
  parseMarkdownFile,
} = require("@docusaurus/utils");

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

function getSourceConnectors() {
  return getFilenamesInDir("sources/", sourcesDocs, [
    "readme",
    "postgres",
    "mongodb-v2",
    "mssql",
    "mysql",
  ]);
}

function getDestinationConnectors() {
  return getFilenamesInDir("destinations/", destinationDocs, [
    "readme",
    "s3",
    "postgres",
  ]);
}

function getEnterpriseConnectors() {
  return getFilenamesInDir("enterprise-connectors/", enterpriseConnectorDocs, [
    "readme",
  ]);
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

const connectorCatalog = {
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
      items: [
        sourcePostgres,
        sourceMongoDB,
        sourceMysql,
        sourceMssql,
        ...getSourceConnectors(),
      ].sort((itemA, itemB) => {
        const labelA = itemA?.label || "";
        const labelB = itemB?.label || "";
        return labelA.localeCompare(labelB);
      }),
    },
    {
      type: "category",
      label: "Destinations",
      link: {
        type: "doc",
        id: "destinations/README",
      },
      items: [
        destinationS3,
        destinationPostgres,
        ...getDestinationConnectors(),
      ].sort((itemA, itemB) => {
        const labelA = itemA?.label || "";
        const labelB = itemB?.label || "";
        return labelA.localeCompare(labelB);
      }),
    },
    {
      type: "category",
      label: "Enterprise Connectors",
      link: {
        type: "doc",
        id: "enterprise-connectors/README",
      },
      items: [...getEnterpriseConnectors()].sort((itemA, itemB) => {
        const labelA = itemA?.label || "";
        const labelB = itemB?.label || "";
        return labelA.localeCompare(labelB);
      }),
    },
    "connector-support-levels",
    {
      type: "doc",
      id: "custom-connectors",
    },
    "locating-files-local-destination",
  ],
};

module.exports = {
  connectors: [connectorCatalog],
};
