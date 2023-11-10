const fetch = require("node-fetch");
const visit = require("unist-util-visit");

const registry_url =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";
let registry = {};
let loading = false;

const plugin = () => {
  const transformer = async (ast, vfile) => {
    if (!isDocsPage(vfile)) return;

    await fetchCatalog();

    const pathParts = vfile.path.split("/");
    const connectorName = pathParts.pop().split(".")[0];
    const connectorType = pathParts.pop();
    const dockerRepository = `airbyte/${connectorType.replace(
      /s$/,
      ""
    )}-${connectorName}`;
    const registryEntry = registry.find(
      (r) => r.dockerRepository_oss === dockerRepository
    );

    if (!registryEntry) return;

    visit(ast, "heading", (node) => {
      let headerFound = false;
      if (node.depth === 1 && node.children.length === 1 && !headerFound) {
        headerFound = true;
        const originalTitle = node.children[0].value;
        const originalId = node.data.hProperties.id;

        node.type = "html";
        node.children = undefined;
        node.value = buildConnectorHTMLContent(
          registryEntry,
          originalTitle,
          originalId
        );
      }
    });
  };
  return transformer;
};

const buildConnectorHTMLContent = (
  registryEntry,
  originalTitle,
  originalId
) => {
  const htmlContent = `
  <h1 id="${originalId}">${originalTitle}</h1>
  <small>
    <table>
      <tbody>
        <tr>
          <td rowSpan="4">
            <img style="max-height: 75px" src="${registryEntry.iconUrl_oss}" />
          </td>
          <td>Support Level: </td>
          <td><strong>${capitalizeFirstLetter(
            registryEntry.supportLevel_oss
          )}</strong></td>
        </tr>
        <tr>
          <td>Definition Id: </td>
          <td>${registryEntry.definitionId}</td>
        </tr>
        <tr>
          <td>Latest Version: </td>
          <td>${registryEntry.dockerImageTag_oss}</td>
        </tr>
        <tr>
          <td>Availability:</td>
          <td>Airbyte Cloud: ${
            registryEntry.is_cloud ? "✅" : "❌"
          }  |  Airbyte OSS: ${registryEntry.is_oss ? "✅" : "❌"}</td>
        </tr>
      </tbody>
    </table>
  </small>
  <br />
`;

  return htmlContent;
};

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

/*
This methods makes registry a singleton available to all callers of this plugin.
Only one download will happen for the first callers and all others will use the cached version.
*/
const fetchCatalog = async () => {
  if (loading) {
    await sleep(500);
    return fetchCatalog();
  }

  if (registry.length > 0) {
    return registry;
  }

  loading = true;
  console.log("Fetching connector registry...");
  const response = await fetch(registry_url);
  registry = await response.json();
  console.log(`fetched ${registry.length} connectors form registry`);
  loading = false;
};

const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
};

module.exports = plugin;
