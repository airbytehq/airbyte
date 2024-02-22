const { catalog } = require("../connector_registry");

const isDocsPage = (vfile) => {
  if (
    !vfile.path.includes("integrations/sources") &&
    !vfile.path.includes("integrations/destinations")
  ) {
    return false;
  }

  // skip the root files in integrations/source and integrations/destinations
  if (vfile.path.includes("README.md")) {
    return false;
  }

  if (vfile.path.includes("-migrations.md")) {
    return false;
  }

  return true;
};

const getRegistryEntry = async (vfile) => {
  const pathParts = vfile.path.split("/");
  const connectorName = pathParts.pop().split(".")[0];
  const connectorType = pathParts.pop();
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
  getRegistryEntry,
};
