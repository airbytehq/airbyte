// Client-side registry utilities
// This works with URLs instead of vfiles and fetches data from the connector registry

const connectorPageAlternativeEndings = ["-migrations", "-troubleshooting"];
const connectorPageAlternativeEndingsRegExp = new RegExp(
  connectorPageAlternativeEndings.join("|"),
  "gi",
);

const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

const fetchRegistry = async () => {
  try {
    const response = await fetch(REGISTRY_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch registry: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch connector registry:", error);
    return [];
  }
};

const getRegistryEntry = async ({ path }) => {
  if (
    !path.includes("integrations/sources") &&
    !path.includes("integrations/destinations")
  ) {
    return;
  }

  // Extract connector info from pathname
  const pathParts = path.split("/");
  const integrationIndex = pathParts.indexOf("integrations");
  if (integrationIndex === -1) return;

  const connectorType = pathParts[integrationIndex + 1]; // "sources" or "destinations"
  const connectorNameWithExt = pathParts[integrationIndex + 2]; // e.g., "mysql.md" or "mysql"

  if (!connectorNameWithExt) return;

  let connectorName = connectorNameWithExt.split(".")[0]; // Remove .md extension

  // Remove alternative endings
  connectorName = connectorName.replace(connectorPageAlternativeEndingsRegExp, "");

  const dockerRepository = `airbyte/${connectorType.replace(/s$/, "")}-${connectorName}`;

  const registry = await fetchRegistry();

  let registryEntry = registry.find(
    (r) => r.dockerRepository_oss === dockerRepository,
  );

  if (!registryEntry) {
    registryEntry = buildArchivedRegistryEntry(
      connectorName,
      dockerRepository,
      connectorType,
    );
  }

  return registryEntry;
};

const buildArchivedRegistryEntry = (
  connectorName,
  dockerRepository,
  connectorType,
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
  getRegistryEntry,
};
