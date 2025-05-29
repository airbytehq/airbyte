const memoize = require("lodash/memoize");

const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

const fetchLatestVersionOfPyPackage = memoize(async (packageName) => {
  const json = await fetch(`https://pypi.org/pypi/${packageName}/json`).then(
    (resp) => resp.json(),
  );
  return json.info.version;
});

const fetchCatalog = async () => {
  console.log("Fetching connector registry...");
  const json = await fetch(REGISTRY_URL).then((resp) => resp.json());
  console.log(`fetched ${json.length} connectors from registry`);
  
  const sapHanaConnectors = json.filter(c => 
    (c.name_oss && c.name_oss.toLowerCase().includes("sap hana")) || 
    (c.name_cloud && c.name_cloud.toLowerCase().includes("sap hana"))
  );
  console.log("SAP HANA connectors found:", sapHanaConnectors.length);
  if (sapHanaConnectors.length > 0) {
    console.log("SAP HANA connector details:", 
      sapHanaConnectors.map(c => ({
        name: c.name_oss || c.name_cloud,
        dockerRepo: c.dockerRepository_oss,
        version: c.dockerImageTag_oss
      }))
    );
  }
  
  const volcanoConnectors = json.filter(c => 
    (c.dockerRepository_oss && c.dockerRepository_oss.toLowerCase().includes("volcano"))
  );
  console.log("Volcano connectors found:", volcanoConnectors.length);
  if (volcanoConnectors.length > 0) {
    console.log("Volcano connector details:", 
      volcanoConnectors.map(c => ({
        name: c.name_oss || c.name_cloud,
        dockerRepo: c.dockerRepository_oss,
        version: c.dockerImageTag_oss
      }))
    );
  }
  
  return json;
};

const getLatestPythonCDKVersion = async () =>
  fetchLatestVersionOfPyPackage("airbyte-cdk");

const parseCDKVersion = (
  connectorCdkVersion,
  latestPythonCdkVersion,
  latestJavaCdkVersion,
) => {
  if (!connectorCdkVersion || !connectorCdkVersion.includes(":")) {
    return { version: connectorCdkVersion, isLatest: false };
  }

  const [language, version] = connectorCdkVersion.split(":");
  switch (language) {
    case "python":
      const isLatest = version === latestPythonCdkVersion;
      const packageUrl = `https://pypi.org/project/airbyte-cdk/${version}/`;
      return { version, isLatest, url: packageUrl };
    case "java":
      return { version, isLatest: version === latestJavaCdkVersion, url: null };
    default:
      return { version, isLatest: false, url: null };
  }
};

function getSupportLevelDisplay(rawSupportLevel) {
  switch (rawSupportLevel) {
    case "certified":
      return "Airbyte";
    case "community":
      return "Marketplace";
    case "enterprise":
      return "Enterprise";
    case "archived":
      return "Archived";
    default:
      return null;
  }
}

module.exports = {
  REGISTRY_URL,
  catalog: fetchCatalog(),
  isPypiConnector: (connector) => {
    return Boolean(connector.remoteRegistries_oss?.pypi?.enabled);
  },
  getLatestPythonCDKVersion,
  parseCDKVersion,
  getSupportLevelDisplay,
};
