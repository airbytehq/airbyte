// Client-side registry utilities
// This works with URLs instead of vfiles and fetches data from the connector registry
//
// Fetches both the OSS and Cloud registries and merges them into a single
// composite list, replacing the legacy connector_registry_report.json dependency.

const connectorPageAlternativeEndings = ["-migrations", "-troubleshooting"];
const connectorPageAlternativeEndingsRegExp = new RegExp(
  connectorPageAlternativeEndings.join("|"),
  "gi",
);

const OSS_REGISTRY_URL =
  "https://connectors.airbyte.com/files/registries/v0/oss_registry.json";
const CLOUD_REGISTRY_URL =
  "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json";

const GITHUB_REPO_NAME = "airbytehq/airbyte";
const CONNECTORS_PATH = "airbyte-integrations/connectors";

function mergeRegistries(ossRegistry, cloudRegistry) {
  const ossSourcesByRepo = new Map();
  for (const src of ossRegistry.sources || []) {
    ossSourcesByRepo.set(src.dockerRepository, src);
  }
  const ossDestsByRepo = new Map();
  for (const dst of ossRegistry.destinations || []) {
    ossDestsByRepo.set(dst.dockerRepository, dst);
  }
  const cloudSourcesByRepo = new Map();
  for (const src of cloudRegistry.sources || []) {
    cloudSourcesByRepo.set(src.dockerRepository, src);
  }
  const cloudDestsByRepo = new Map();
  for (const dst of cloudRegistry.destinations || []) {
    cloudDestsByRepo.set(dst.dockerRepository, dst);
  }

  const allSourceRepos = new Set([
    ...ossSourcesByRepo.keys(),
    ...cloudSourcesByRepo.keys(),
  ]);
  const allDestRepos = new Set([
    ...ossDestsByRepo.keys(),
    ...cloudDestsByRepo.keys(),
  ]);

  const merged = [];

  for (const repo of allSourceRepos) {
    const oss = ossSourcesByRepo.get(repo) || null;
    const cloud = cloudSourcesByRepo.get(repo) || null;
    merged.push(buildCompositeEntry(oss, cloud, "source", repo));
  }

  for (const repo of allDestRepos) {
    const oss = ossDestsByRepo.get(repo) || null;
    const cloud = cloudDestsByRepo.get(repo) || null;
    merged.push(buildCompositeEntry(oss, cloud, "destination", repo));
  }

  return merged;
}

function buildCompositeEntry(oss, cloud, connectorType, dockerRepository) {
  const connectorName = dockerRepository.replace("airbyte/", "");
  const definitionId =
    oss?.sourceDefinitionId ||
    oss?.destinationDefinitionId ||
    cloud?.sourceDefinitionId ||
    cloud?.destinationDefinitionId ||
    "";

  const githubUrl = `https://github.com/${GITHUB_REPO_NAME}/blob/master/${CONNECTORS_PATH}/${connectorName}`;
  const issuesLabel = `connectors/${connectorType}/${connectorName.replace(`${connectorType}-`, "")}`;
  const issueUrl = `https://github.com/${GITHUB_REPO_NAME}/issues?q=is:open+is:issue+label:${issuesLabel}`;

  return {
    connector_type: connectorType,
    definitionId,
    is_oss: oss != null,
    is_cloud: cloud != null,
    github_url: githubUrl,
    issue_url: issueUrl,

    name_oss: oss?.name || cloud?.name || "",
    dockerRepository_oss: oss?.dockerRepository || dockerRepository,
    dockerImageTag_oss: oss?.dockerImageTag || "",
    supportLevel_oss: oss?.supportLevel || cloud?.supportLevel || "community",
    iconUrl_oss: oss?.iconUrl || cloud?.iconUrl || "",
    documentationUrl_oss: oss?.documentationUrl || cloud?.documentationUrl || "",

    name_cloud: cloud?.name || oss?.name || "",
    dockerRepository_cloud: cloud?.dockerRepository || "",
    dockerImageTag_cloud: cloud?.dockerImageTag || "",
    supportLevel_cloud: cloud?.supportLevel || "",
    documentationUrl_cloud: cloud?.documentationUrl || "",
  };
}

const fetchRegistry = async () => {
  try {
    const [ossResponse, cloudResponse] = await Promise.all([
      fetch(OSS_REGISTRY_URL),
      fetch(CLOUD_REGISTRY_URL),
    ]);
    if (!ossResponse.ok) {
      throw new Error(`Failed to fetch OSS registry: ${ossResponse.statusText}`);
    }
    if (!cloudResponse.ok) {
      throw new Error(`Failed to fetch Cloud registry: ${cloudResponse.statusText}`);
    }
    const [ossRegistry, cloudRegistry] = await Promise.all([
      ossResponse.json(),
      cloudResponse.json(),
    ]);
    return mergeRegistries(ossRegistry, cloudRegistry);
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
