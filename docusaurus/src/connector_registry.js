const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

const fetchCatalog = async () => {
  console.log("Fetching connector registry...");
  const json = await fetch(REGISTRY_URL).then((resp) => resp.json());
  console.log(`fetched ${json.length} connectors form registry`);
  return json;
};

module.exports = {
  catalog: fetchCatalog(),
  isPypiConnector: (connector) => {
    // TODO: Look for remoteRegistries here instead of hardcoded list
    return [
      "airbyte/source-google-sheets",
      "airbyte/source-facebook-marketing",
      "airbyte/source-salesforce",
      "airbyte/source-shopify",
      "airbyte/source-s3",
      "airbyte/source-stripe",
      "airbyte/source-google-ads",
    ].includes(connector.dockerRepository_oss)
    // return Boolean(connector.remoteRegistries?.pypi?.enabled);
  }
}
