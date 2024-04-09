import React from "react";
import { useEffect, useState } from "react";

import styles from "./ConnectorRegistry.module.css";
import { REGISTRY_URL } from "../connector_registry";

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
  if (a.supportLevel_oss !== b.supportLevel_oss) {
    if (a.supportLevel_oss === "certified") return -3;
    if (b.supportLevel_oss === "certified") return 3;
    if (a.supportLevel_oss === "community") return -2;
    if (b.supportLevel_oss === "community") return 2;
    if (a.supportLevel_oss === "archived") return -1;
    if (b.supportLevel_oss === "archived") return 1;
  }

  if (a.name_oss < b.name_oss) return -1;
  if (a.name_oss > b.name_oss) return 1;
}

export default function ConnectorRegistry({ type }) {
  const [registry, setRegistry] = useState([]);

  useEffect(() => {
    fetchCatalog(REGISTRY_URL, setRegistry);
  }, []);

  if (registry.length === 0) return <div>{`Loading ${type}s...`}</div>;

  const connectors = registry
    .filter((c) => c.connector_type === type)
    .filter((c) => c.name_oss)
    .filter((c) => c.supportLevel_oss); // at lease one connector is missing a support level

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Connector Name</th>
            <th>Links</th>
            <th>Support Level</th>
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
                  <div className={styles.connectorName}>
                    {connector.iconUrl_oss && (
                      <img src={connector.iconUrl_oss} style={iconStyle} />
                    )}
                    <a href={docsLink}>{connector.name_oss}</a>
                  </div>
                </td>
                {/* min width to prevent wrapping */}
                <td style={{ minWidth: 75 }}>
                  <a href={docsLink}>📕</a>
                  {connector.supportLevel_oss != "archived" ? (
                    <a href={connector.github_url}>⚙️</a>
                  ) : (
                    ""
                  )}
                  {connector.supportLevel_oss != "archived" ? (
                    <a href={connector.issue_url}>🐛</a>
                  ) : null}
                </td>
                <td>
                  <small>{connector.supportLevel_oss}</small>
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
