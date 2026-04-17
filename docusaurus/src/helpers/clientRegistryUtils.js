// Client-side registry utilities
// This works with URLs instead of vfiles and fetches data from the connector registry
//
// Fetches the composite connector registry (a server-side superset of the OSS
// and Cloud registries) and projects each entry into the `_oss` / `_cloud`
// suffixed shape that downstream consumers expect.

const connectorPageAlternativeEndings = ["-migrations", "-troubleshooting"];
const connectorPageAlternativeEndingsRegExp = new RegExp(
  connectorPageAlternativeEndings.join("|"),
  "gi",
);

const COMPOSITE_REGISTRY_URL =
  "https://connectors.airbyte.com/files/registries/v0/composite_registry.json";

const GITHUB_REPO_NAME = "airbytehq/airbyte";
const CONNECTORS_PATH = "airbyte-integrations/connectors";

function buildCompositeEntry(entry, connectorType) {
  const dockerRepository = entry.dockerRepository || "";
  const connectorName = dockerRepository.replace("airbyte/", "");
  const definitionId =
    entry.sourceDefinitionId || entry.destinationDefinitionId || "";
  const availability = entry.availability || [];
  const isOss = availability.includes("oss");
  const isCloud = availability.includes("cloud");

  const githubUrl = `https://github.com/${GITHUB_REPO_NAME}/blob/master/${CONNECTORS_PATH}/${connectorName}`;
  const issuesLabel = `connectors/${connectorType}/${connectorName.replace(`${connectorType}-`, "")}`;
  const issueUrl = `https://github.com/${GITHUB_REPO_NAME}/issues?q=is:open+is:issue+label:${issuesLabel}`;

  return {
    connector_type: connectorType,
    definitionId,
    is_oss: isOss,
    is_cloud: isCloud,
    github_url: githubUrl,
    issue_url: issueUrl,

    name_oss: entry.name || "",
    dockerRepository_oss: dockerRepository,
    dockerImageTag_oss: entry.dockerImageTag || "",
    supportLevel_oss: entry.supportLevel || "community",
    iconUrl_oss: entry.iconUrl || "",
    documentationUrl_oss: entry.documentationUrl || "",

    name_cloud: entry.name || "",
    dockerRepository_cloud: dockerRepository,
    dockerImageTag_cloud: entry.dockerImageTag || "",
    supportLevel_cloud: entry.supportLevel || "",
    documentationUrl_cloud: entry.documentationUrl || "",
  };
}

const fetchRegistry = async () => {
  try {
    const response = await fetch(COMPOSITE_REGISTRY_URL);
    if (!response.ok) {
      throw new Error(
        `Failed to fetch composite registry: ${response.statusText}`,
      );
    }
    const compositeRegistry = await response.json();
    const sources = compositeRegistry.sources || [];
    const destinations = compositeRegistry.destinations || [];
    return [
      ...sources.map((entry) => buildCompositeEntry(entry, "source")),
      ...destinations.map((entry) => buildCompositeEntry(entry, "destination")),
    ];
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
