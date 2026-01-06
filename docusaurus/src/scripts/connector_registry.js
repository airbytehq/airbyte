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
      const packageUrl = `https://pypi.org/project/airbyte-cdk/${version}/`;
      return { version, url: packageUrl };
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
  isPypiConnector: (connector) => {
    return Boolean(connector.remoteRegistries_oss?.pypi?.enabled);
  },
  parseCDKVersion,
  getSupportLevelDisplay,
};
