const fs = require("fs");
const path = require("path");
const { fetchRegistry } = require("./fetch-registry");
const { toSafeLogString } = require("./log-safe");

const CONNECTOR_SPECS_DIR = path.join(
  __dirname,
  "..",
  "..",
  "static",
  "connector-specs",
);

function sortObjectKeys(value) {
  if (Array.isArray(value)) {
    return value.map(sortObjectKeys);
  }

  if (value && typeof value === "object") {
    return Object.keys(value)
      .sort()
      .reduce((sorted, key) => {
        sorted[key] = sortObjectKeys(value[key]);
        return sorted;
      }, {});
  }

  return value;
}

function writeJson(filePath, value) {
  fs.writeFileSync(
    filePath,
    `${JSON.stringify(sortObjectKeys(value), null, 2)}\n`,
  );
}

function clearGeneratedAssets() {
  for (const fileName of fs.readdirSync(CONNECTOR_SPECS_DIR)) {
    if (fileName.endsWith(".json")) {
      fs.unlinkSync(path.join(CONNECTOR_SPECS_DIR, fileName));
    }
  }
}

function isUsableConnectionSpecification(specification) {
  return (
    specification &&
    typeof specification === "object" &&
    !Array.isArray(specification)
  );
}

function compareConnectors(left, right) {
  const byName = left.name.localeCompare(right.name, "en", {
    sensitivity: "base",
  });
  if (byName !== 0) {
    return byName;
  }

  return left.definitionId.localeCompare(right.definitionId);
}

async function main() {
  fs.mkdirSync(CONNECTOR_SPECS_DIR, { recursive: true });
  clearGeneratedAssets();

  const registry = await fetchRegistry();
  const index = [];
  let skippedCount = 0;

  for (const connector of registry) {
    const specification = connector.spec?.connectionSpecification;
    if (!isUsableConnectionSpecification(specification)) {
      skippedCount += 1;
      console.warn(
        `Skipping ${toSafeLogString(connector.name || connector.dockerRepository || "connector")}: ` +
          "no usable connectionSpecification",
      );
      continue;
    }

    const { definitionId } = connector;
    if (
      typeof definitionId !== "string" ||
      !definitionId ||
      !/^[a-zA-Z0-9._-]+$/.test(definitionId)
    ) {
      skippedCount += 1;
      console.warn(
        `Skipping ${toSafeLogString(connector.name || connector.dockerRepository || "connector")}: ` +
          "missing or invalid definitionId",
      );
      continue;
    }

    const name = connector.name || connector.dockerRepository || definitionId;
    const indexEntry = {
      definitionId,
      name,
      connector_type: connector.connector_type,
      dockerRepository: connector.dockerRepository,
      documentationUrl: connector.documentationUrl,
    };

    writeJson(
      path.join(CONNECTOR_SPECS_DIR, `${definitionId}.json`),
      specification,
    );
    index.push(indexEntry);
  }

  index.sort(compareConnectors);
  writeJson(path.join(CONNECTOR_SPECS_DIR, "index.json"), index);

  console.log(
    `✓ Wrote ${index.length} connector specs and index to ${CONNECTOR_SPECS_DIR}`,
  );
  if (skippedCount > 0) {
    console.warn(`Skipped ${skippedCount} connectors`);
  }
}

main().catch((error) => {
  console.error(
    `Error preparing connector spec assets: ${toSafeLogString(error)}`,
  );
  process.exit(1);
});
