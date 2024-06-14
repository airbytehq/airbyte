const memoize = require("lodash/memoize");


const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

const fetchLatestVersionOfPyPackage = memoize(async (packageName) => {
  const json = await fetch(
    `https://pypi.org/pypi/${packageName}/json`
  ).then((resp) => resp.json());
  return json.info.version;
});

const fetchCatalog = async () => {
  console.log("Fetching connector registry...");
  const json = await fetch(REGISTRY_URL).then((resp) => resp.json());
  console.log(`fetched ${json.length} connectors form registry`);
  return json;
};

const getLatestPythonCDKVersion = async () => fetchLatestVersionOfPyPackage("airbyte-cdk");

const parseCDKVersion = (connectorCdkVersion, latestPythonCdkVersion, latestJavaCdkVersion) => {
  if (!connectorCdkVersion || !connectorCdkVersion.includes(":")) {
    return { version: connectorCdkVersion, isLatest: false };
  }

  const [language, version] = connectorCdkVersion.split(":");
  switch (language) {
    case "python":
      const isLatest = version === latestPythonCdkVersion;
      const packageUrl = `https://pypi.org/project/airbyte-cdk/${version}/`;
      return { version, isLatest, url: packageUrl};
    case "java":
      return { version, isLatest: version === latestJavaCdkVersion, url: null};
    default:
      return { version, isLatest: false, url: null};
  }
};

module.exports = {
  REGISTRY_URL,
  catalog: fetchCatalog(),
  isPypiConnector: (connector) => {
    return Boolean(connector.remoteRegistries_oss?.pypi?.enabled);
  },
  getLatestPythonCDKVersion,
  parseCDKVersion,
};
