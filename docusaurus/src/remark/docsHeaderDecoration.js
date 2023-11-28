const fetch = require("node-fetch");
const visit = require("unist-util-visit");

const CHECK_ICON = `<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><title>Available</title><path fill="currentColor" d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-111 111-47-47c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l64 64c9.4 9.4 24.6 9.4 33.9 0L369 209z"/></svg>`;
const CROSS_ICON = `<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><title>Not available</title><path fill="currentColor" d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>`;

const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

const fetchCatalog = async () => {
  console.log("Fetching connector registry...");
  const json = await fetch(REGISTRY_URL).then((resp) => resp.json());
  console.log(`fetched ${json.length} connectors form registry`);
  return json;
};

const catalog = fetchCatalog();

const plugin = () => {
  const transformer = async (ast, vfile) => {
    if (!isDocsPage(vfile)) return;

    const pathParts = vfile.path.split("/");
    const connectorName = pathParts.pop().split(".")[0];
    const connectorType = pathParts.pop();
    const dockerRepository = `airbyte/${connectorType.replace(
      /s$/,
      ""
    )}-${connectorName}`;

    const registry = await catalog;

    const registryEntry = registry.find(
      (r) => r.dockerRepository_oss === dockerRepository
    );

    if (!registryEntry) return;

    visit(ast, "heading", (node) => {
      if (node.depth === 1 && node.children.length === 1) {
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
  // note - you can't have any leading whitespace here
  const htmlContent = `<div>
    <dl class="connectorMetadata">
      <div>
        <dt>Availability</dt>
        <dd class="availability">
          <span class="${
            registryEntry.is_cloud ? "available" : "unavailable"
          }">${
    registryEntry.is_cloud ? CHECK_ICON : CROSS_ICON
  } Airbyte Cloud</span>
          <span class="${registryEntry.is_oss ? "available" : "unavailable"}">${
    registryEntry.is_oss ? CHECK_ICON : CROSS_ICON
  } Airbyte OSS</span>
        </dd>
      </div>
      <div>
        <dt>Support Level</dt>
        <dd>
          <a href="/project-overview/product-support-levels/">${escape(
            capitalizeFirstLetter(registryEntry.supportLevel_oss)
          )}</a>
        </dd>
      </div>
      <div>
        <dt>Latest Version</dt>
        <dd>${escape(registryEntry.dockerImageTag_oss)}</dd>
      </div>
    </dl>

    <div class="header">
      <img src="${registryEntry.iconUrl_oss}" alt="" class="connectorIcon"  />
      <h1 id="${originalId}">${originalTitle}</h1>
    </div>
  </div>`;

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

const escape = (string) => {
  return string
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
};

const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
};

module.exports = plugin;
