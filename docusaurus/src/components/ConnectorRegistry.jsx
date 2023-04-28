import React from "react";
import { useEffect, useState } from "react";

const oss_registry_url =
  "https://connectors.airbyte.com/api/v0/catalog/oss_catalog.json";
const cloud_registry_url =
  "https://connectors.airbyte.com/api/v0/catalog/cloud_catalog.json";
const iconBase =
  "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-config-oss/init-oss/src/main/resources/icons";
const iconStyle = { maxWidth: 25 };
const sourceBase =
  "https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors";
const bugsBase =
  "https://github.com/airbytehq/airbyte/issues?q=is:open+is:issue+label"; // :connectors/source/activecampaign

function fetchCatalog(url, setter) {
  const response = await fetch(url);
  const registry = await response.json();
  setter(registry);
}

/*
Sorts connectors by release stage and then name
*/
function connectorSort(a, b) {
  if (a.releaseStage !== b.releaseStage) {
    if (a.releaseStage === "generally_available") return -3;
    if (b.releaseStage === "generally_available") return 3;
    if (a.releaseStage === "beta") return -2;
    if (b.releaseStage === "beta") return 2;
    if (a.releaseStage === "alpha") return -1;
    if (b.releaseStage === "alpha") return 1;
  }

  if (a.name < b.name) return -1;
  if (a.name > b.name) return 1;
}

export default function ConnectorRegistry({ type }) {
  const [ossRegistry, setOssRegistry] = useState([]);
  const [cloudRegistry, setCloudRegistry] = useState([]);

  useEffect(() => {
    fetchCatalog(oss_registry_url, setOssRegistry);
    fetchCatalog(cloud_registry_url, setCloudRegistry);
  }, []);

  if (ossRegistry.length === 0 || cloudRegistry.length === 0)
    return <div>{`Loading ${type}s...`}</div>;

  // makes the assumption that the OSS registry is a superset of the cloud registry
  const connectors = ossRegistry[type + "s"];

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Connector Name</th>
            <th>Icon</th>
            <th>Links</th>
            <th>Release Stage</th>
            <th>OSS</th>
            <th>Cloud</th>
            <th>Docker Image</th>
          </tr>
        </thead>
        <tbody>
          {connectors.sort(connectorSort).map((connector) => {
            const baseName = connector.dockerRepository.replace("airbyte/", "");
            const codeName = baseName
              .replace("source-", "")
              .replace("destination-", "");
            const iconLink = `${iconBase}/${connector.icon}`;
            const docsLink = `/integrations/${type}s/${codeName}`; // not using documentationUrl so we can have relative links
            const sourceLink = `${sourceBase}/${baseName}`;
            const bugsLink = `${bugsBase}:connectors/${type}/${codeName}`;
            const isCloud = cloudRegistry[type + "s"].find(
              (c) => c.name === connector.name
            );

            return (
              <tr key={`${type}-${baseName}`}>
                <td>
                  <strong>
                    <a href={docsLink}>{connector.name}</a>
                  </strong>
                </td>
                <td>
                  {connector.icon ? (
                    <img src={iconLink} style={iconStyle} />
                  ) : null}
                </td>
                {/* min width to prevent wrapping */}
                <td style={{ minWidth: 75 }}>
                  <a href={docsLink}>📕</a>
                  <a href={sourceLink}>⚙️</a>
                  <a href={bugsLink}>🐛</a>
                </td>
                <td>
                  <small>{connector.releaseStage}</small>
                </td>
                <td>✅</td>
                <td>{isCloud ? "✅" : "❌"}</td>
                <td>
                  <small>
                    <code>
                      {connector.dockerRepository}:{connector.dockerImageTag}
                    </code>
                  </small>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
