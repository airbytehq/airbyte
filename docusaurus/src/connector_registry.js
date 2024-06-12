const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

const fetchCatalog = async () => {
  console.log("Fetching connector registry...");
  const json = await fetch(REGISTRY_URL).then((resp) => resp.json());
  console.log(`fetched ${json.length} connectors form registry`);
  return json;
};

module.exports = {
  REGISTRY_URL,
  catalog: fetchCatalog(),
  isPypiConnector: (connector) => {
    return Boolean(connector.remoteRegistries_oss?.pypi?.enabled);
  },
};
