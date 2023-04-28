import React from "react";
import { useEffect, useState } from "react";

const registry_url =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

const iconStyle = { maxWidth: 25 };

async function fetchCatalog(url, setter) {
  const response = await fetch(url);
  const registry = await response.json();
  setter(registry);
}

/*
Sorts connectors by release stage and then name
*/
function connectorSort(a, b) {
  if (a.releaseStage_oss !== b.releaseStage_oss) {
    if (a.releaseStage_oss === "generally_available") return -3;
    if (b.releaseStage_oss === "generally_available") return 3;
    if (a.releaseStage_oss === "beta") return -2;
    if (b.releaseStage_oss === "beta") return 2;
    if (a.releaseStage_oss === "alpha") return -1;
    if (b.releaseStage_oss === "alpha") return 1;
  }

  if (a.name_oss < b.name_oss) return -1;
  if (a.name_oss > b.name_oss) return 1;
}

export default function ConnectorRegistry({ type }) {
  const [registry, setRegistry] = useState([]);

  useEffect(() => {
    fetchCatalog(registry_url, setRegistry);
  }, []);

  if (registry.length === 0) return <div>{`Loading ${type}s...`}</div>;

  const connectors = registry
    .filter((c) => c.connector_type === type)
    .filter((c) => c.name_oss);

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
            const docsLink = connector.documentationUrl_oss?.replace(
              "https://docs.airbyte.com",
              ""
            ); // not using documentationUrl so we can have relative links

            return (
              <tr key={`${connector.definitionId}`}>
                <td>
                  <strong>
                    <a href={docsLink}>{connector.name_oss}</a>
                  </strong>
                </td>
                <td>
                  {connector.icon_url ? (
                    <img src={connector.icon_url} style={iconStyle} />
                  ) : null}
                </td>
                {/* min width to prevent wrapping */}
                <td style={{ minWidth: 75 }}>
                  <a href={docsLink}>📕</a>
                  <a href={connector.github_url}>⚙️</a>
                  <a href={connector.issue_url}>🐛</a>
                </td>
                <td>
                  <small>{connector.releaseStage_oss}</small>
                </td>
                <td>{connector.is_oss ? "✅" : "❌"}</td>
                <td>{connector.is_cloud ? "✅" : "❌"}</td>
                <td>
                  <small>
                    <code>
                      {connector.dockerRepository_oss}:
                      {connector.dockerImageTag_oss}
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
