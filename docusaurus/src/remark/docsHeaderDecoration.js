const fetch = require("node-fetch");
const visit = require("unist-util-visit");

const registry_url =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";
let registry = {};
let loading = false;

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

    let originalTitle = "";
    let originalId = "";

    visit(ast, "heading", (node) => {
      if (node.depth === 1 && node.children.length === 1) {
        originalTitle = node.children[0].value;
        originalId = node.data.hProperties.id;

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
  <div>
    <div class="header">
      <img src="${
        registryEntry.iconUrl_oss
      }" alt="connector logo" style="max-height: 40px; max-width: 40px; float: left; margin-right: 10px" />
      <h1 id="${originalId}" style="position: relative;">${originalTitle}</h1>
    </div>

    <small>
      <div style="width: 100%; background-color: rgb(220 220 220 / 25%); margin-bottom: 5px">
        <strong>Availability</strong>: Airbyte Cloud: ${
          registryEntry.is_cloud ? "✅" : "❌"
        }, Airbyte OSS: ${registryEntry.is_oss ? "✅" : "❌"}
        <br />
        <strong>Support Level</strong>: <a href="/project-overview/product-support-levels/">${capitalizeFirstLetter(
          registryEntry.supportLevel_oss
        )}</a>
        <br />
        <strong>Latest Version</strong>: ${registryEntry.dockerImageTag_oss}
        <br />
        <strong>Definition Id</strong>: ${registryEntry.definitionId}
      </div>
    </small>
  </div>
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

const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
};

module.exports = plugin;
