const { catalog } = require("../connector_registry");

// the migration guide and troubleshooting guide are not connectors, but also not in a sub-folder, e.g. /integrations/sources/mssql-migrations
const connectorPageAlternativeEndings = ["-migrations", "-troubleshooting"];
const connectorPageAlternativeEndingsRegExp = new RegExp(
  connectorPageAlternativeEndings.join("|"),
  "gi"
);

const isDocsPage = (vfile) => {
  let response = { isDocsPage: false, isTrueDocsPage: false };

  if (
    (vfile.path.includes("integrations/sources") ||
      vfile.path.includes("integrations/destinations")) &&
    !vfile.path.toLowerCase().includes("readme.md")
  ) {
    response.isDocsPage = true;
    response.isTrueDocsPage = true;
  }

  if (response.isDocsPage === true) {
    for (const ending of connectorPageAlternativeEndings) {
      if (vfile.path.includes(ending)) {
        response.isTrueDocsPage = false;
      }
    }
  }

  return response;
};

const isEnterpriseConnectorDocsPage = (vfile) => {
  if (
    vfile.path.includes("integrations/enterprise-connectors") &&
    !vfile.path.toLowerCase().includes("readme.md")
  ) {
    return true;
  }

  return false;
};

const getRegistryEntry = async (vfile) => {
  if (
    !vfile.path.includes("integrations/sources") &&
    !vfile.path.includes("integrations/destinations")
  ) {
    return;
  }

  // troubleshooting pages are sub-pages, but migration pages are not?
  // ["sources", "mysql"] vs ["sources", "mysql", "troubleshooting"] vs ["sources", "mysql-migrations"]
  const pathParts = vfile.path.split("/");
  while (pathParts[0] !== "integrations") pathParts.shift();
  pathParts.shift();
  const connectorType = pathParts.shift();
  const connectorName = pathParts
    .shift()
    .split(".")[0]
    .replace(connectorPageAlternativeEndingsRegExp, "");

  const dockerRepository = `airbyte/${connectorType.replace(
    /s$/,
    ""
  )}-${connectorName}`;

  const registry = await catalog;

  let registryEntry = registry.find(
    (r) => r.dockerRepository_oss === dockerRepository
  );

  if (!registryEntry) {
    registryEntry = buildArchivedRegistryEntry(
      connectorName,
      dockerRepository,
      connectorType
    );
  }

  return registryEntry;
};

const buildArchivedRegistryEntry = (
  connectorName,
  dockerRepository,
  connectorType
) => {
  const dockerName = dockerRepository.split("/")[1];
  const registryEntry = {
    connectorName,
    name_oss: dockerName,
    dockerRepository_oss: dockerRepository,
    is_oss: false,
    is_cloud: false,
    iconUrl_oss: `https://connectors.airbyte.com/files/metadata/airbyte/${dockerName}/latest/icon.svg`,
    supportLevel_oss: "archived",
    documentationUrl_oss: `https://docs.airbyte.com/integrations/${connectorType}s/${connectorName}`,
  };

  return registryEntry;
};

module.exports = {
  isDocsPage,
  isEnterpriseConnectorDocsPage,
  getRegistryEntry,
};
