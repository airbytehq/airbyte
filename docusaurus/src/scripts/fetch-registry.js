/**
 * Utility to manage connector registry - fetching, caching, and extracting minimal data.
 *
 * Fetches both the OSS and Cloud registries from the CDN and merges them
 * into a single composite list with `_oss` / `_cloud` suffixed fields.
 * This replaces the previous dependency on the legacy
 * `connector_registry_report.json` (which is no longer regenerated).
 */
const fs = require("fs");
const https = require("https");
const { DATA_DIR, REGISTRY_CACHE_PATH, OSS_REGISTRY_URL, CLOUD_REGISTRY_URL } = require("./constants");

const GITHUB_REPO_NAME = "airbytehq/airbyte";
const CONNECTORS_PATH = "airbyte-integrations/connectors";

function fetchJsonFromUrl(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Failed to fetch ${url}: ${response.statusCode}`));
          return;
        }

        let data = "";

        response.on("data", (chunk) => {
          data += chunk;
        });

        response.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (error) {
            reject(
              new Error(`Failed to parse data from ${url}: ${error.message}`),
            );
          }
        });
      })
      .on("error", (error) => {
        reject(new Error(`Network error fetching ${url}: ${error.message}`));
      });
  });
}

/**
 * Merge the OSS and Cloud registries into a single flat list of connectors,
 * with `_oss` / `_cloud` suffixed fields matching the shape that downstream
 * consumers (remark plugins, sidebar, ConnectorRegistry.jsx) expect.
 */
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

    // OSS fields
    name_oss: oss?.name || cloud?.name || "",
    dockerRepository_oss: oss?.dockerRepository || dockerRepository,
    dockerImageTag_oss: oss?.dockerImageTag || "",
    supportLevel_oss: oss?.supportLevel || cloud?.supportLevel || "community",
    iconUrl_oss: oss?.iconUrl || cloud?.iconUrl || "",
    documentationUrl_oss: oss?.documentationUrl || cloud?.documentationUrl || "",
    spec_oss: oss?.spec || null,
    remoteRegistries_oss: oss?.remoteRegistries || {},
    packageInfo_oss: oss?.packageInfo || null,
    generated_oss: oss?.generated || null,

    // Cloud fields
    name_cloud: cloud?.name || oss?.name || "",
    dockerRepository_cloud: cloud?.dockerRepository || "",
    dockerImageTag_cloud: cloud?.dockerImageTag || "",
    supportLevel_cloud: cloud?.supportLevel || "",
    documentationUrl_cloud: cloud?.documentationUrl || "",
    packageInfo_cloud: cloud?.packageInfo || null,
    generated_cloud: cloud?.generated || null,
  };
}

async function fetchConnectorRegistriesFromRemote() {
  console.log("Fetching OSS and Cloud connector registries...");
  const [ossRegistry, cloudRegistry] = await Promise.all([
    fetchJsonFromUrl(OSS_REGISTRY_URL),
    fetchJsonFromUrl(CLOUD_REGISTRY_URL),
  ]);
  console.log(
    `Fetched ${(ossRegistry.sources || []).length + (ossRegistry.destinations || []).length} OSS connectors, ` +
    `${(cloudRegistry.sources || []).length + (cloudRegistry.destinations || []).length} Cloud connectors`,
  );
  return mergeRegistries(ossRegistry, cloudRegistry);
}

function extractMinimalRegistryData(fullRegistry) {
  return fullRegistry.map((connector) => ({
    id: (connector.name_oss || connector.name_cloud)
      ?.toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, ""),
    // Properties used by sidebar-connectors.js
    docUrl:
      connector.documentationUrl_cloud || connector.documentationUrl_oss || "",
    supportLevel:
      connector.supportLevel_cloud || connector.supportLevel_oss || "community",
    // Properties used by remark/utils.js and remark/specDecoration.js
    dockerRepository_oss: connector.dockerRepository_oss || "",
    spec_oss: connector.spec_oss
      ? {
          connectionSpecification: connector.spec_oss.connectionSpecification,
        }
      : null,
    // Properties used by remark/utils.js for buildArchivedRegistryEntry
    name_oss: connector.name_oss || connector.name || "",
    is_oss: connector.is_oss || false,
    is_cloud: connector.is_cloud || false,
    iconUrl_oss: connector.iconUrl_oss || "",
    supportLevel_oss: connector.supportLevel_oss || "community",
    documentationUrl_oss: connector.documentationUrl_oss || "",
    // Properties used by remark/connectorList.js (isPypiConnector)
    remoteRegistries_oss: connector.remoteRegistries_oss || {},
    // Properties used by remark/docsHeaderDecoration.js for HeaderDecoration component
    dockerImageTag_oss: connector.dockerImageTag_oss || "",
    github_url: connector.github_url || "",
    issue_url: connector.issue_url || "",
    definitionId: connector.definitionId || "",
    packageInfo_oss: connector.packageInfo_oss || null,
    packageInfo_cloud: connector.packageInfo_cloud || null,
    generated_oss: connector.generated_oss || null,
    generated_cloud: connector.generated_cloud || null,
    // Properties used by ConnectorRegistry.jsx (client-side catalog page)
    connector_type: connector.connector_type || "",
    dockerRepository_cloud: connector.dockerRepository_cloud || "",
    dockerImageTag_cloud: connector.dockerImageTag_cloud || "",
    supportLevel_cloud: connector.supportLevel_cloud || "",
    documentationUrl_cloud: connector.documentationUrl_cloud || "",
    name_cloud: connector.name_cloud || "",
  }));
}

async function fetchRegistry() {
  // Check if cache already exists
  if (fs.existsSync(REGISTRY_CACHE_PATH)) {
    const cachedData = fs.readFileSync(REGISTRY_CACHE_PATH, "utf8");
    const minimalRegistry = JSON.parse(cachedData);
    return minimalRegistry;
  }

  // Fetch both registries and merge if cache doesn't exist
  const fullRegistry = await fetchConnectorRegistriesFromRemote();
  const minimalRegistry = extractMinimalRegistryData(fullRegistry);

  // Ensure data directory exists
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  // Save the minimal registry cache
  fs.writeFileSync(
    REGISTRY_CACHE_PATH,
    JSON.stringify(minimalRegistry, null, 2),
  );
  console.log(`✓ Cached ${minimalRegistry.length} connectors`);

  return minimalRegistry;
}

module.exports = {
  fetchRegistry,
  fetchConnectorRegistriesFromRemote,
  extractMinimalRegistryData,
};
