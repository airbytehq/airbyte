const { archivedConnectors } = require("../components/archivedConnectors");
const { catalog } = require("../connector_registry");

const derivedArchivedConnectorsList = [];

const isDocsPage = (vfile) => {
  if (
    !vfile.path.includes("integrations/sources") &&
    !vfile.path.includes("integrations/destinations")
  ) {
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
    registryEntry = archivedConnectors.find(
      (c) => c.dockerRepository_oss === dockerRepository
    );

    list.push(dockerRepository);
  }

  return registryEntry;
};

module.exports = {
  isDocsPage,
  getRegistryEntry,
  derivedArchivedConnectorsList,
};
