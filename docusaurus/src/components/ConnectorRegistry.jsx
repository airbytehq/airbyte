import { usePluginData } from "@docusaurus/useGlobalData";
import TabItem from "@theme/TabItem";
import Tabs from "@theme/Tabs";
import React, { useEffect, useState } from "react";
import { REGISTRY_URL } from "../connector_registry";
import styles from "./ConnectorRegistry.module.css";

const iconStyle = { maxWidth: 25, maxHeight: 25 };

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

function ConnectorTable({ connectors, connectorSupportLevel }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Connector Name</th>
          <th>Links</th>
          <th>Self-managed</th>
          <th>Cloud</th>
          {connectorSupportLevel !== "enterprise" && <th>Docker Image</th>}
        </tr>
      </thead>
      <tbody>
        {connectors
          .sort(connectorSort)
          .filter(
            (c) =>
              connectorSupportLevel === "enterprise" ||
              c.supportLevel_oss === connectorSupportLevel,
          )
          .map((connector) => {
            const docsLink = connector.documentationUrl_oss?.replace(
              "https://docs.airbyte.com",
              "",
            ); // not using documentationUrl so we can have relative links

            return (
              <tr key={`${connector.definitionId}`}>
                <td>
                  <div className={styles.connectorName}>
                    {connector.iconUrl_oss && (
                      <div className={styles.connectorIconBackground}>
                        <img src={connector.iconUrl_oss} style={iconStyle} />
                      </div>
                    )}

                    <a href={docsLink}>{connector.name_oss}</a>
                  </div>
                </td>
                {/* min width to prevent wrapping */}
                <td style={{ minWidth: 90 }}>
                  <div
                    style={{
                      display: "flex",
                      gap: "8px",
                      justifyContent: "center",
                    }}
                  >
                    <a href={docsLink}>📕</a>
                    {connector.supportLevel_oss != "archived" &&
                    connector.github_url  ? (
                      <a href={connector.github_url}>⚙️</a>
                    ) : (
                      ""
                    )}
                    {connector.supportLevel_oss != "archived" ? (
                      <a href={connector.issue_url}>🐛</a>
                    ) : null}
                  </div>
                </td>
                <td>{connector.is_oss ? "✅" : "❌"}</td>
                <td>{connector.is_cloud ? "✅" : "❌"}</td>
                {connectorSupportLevel !== "enterprise" && (
                  <td>
                    <small>
                      <code>
                        {connector.dockerRepository_oss}:
                      {connector.dockerImageTag_oss}
                    </code>
                    </small>
                  </td>
                )}
              </tr>
            );
          })}
      </tbody>
    </table>
  );
}

export default function ConnectorRegistry({ type }) {
  const pluginData = usePluginData("enterprise-connectors-plugin");
  const [registry, setRegistry] = useState([]);
  const [enterpriseConnectors, setEnterpriseConnectors] = useState([]);

  useEffect(() => {
    fetchCatalog(REGISTRY_URL, setRegistry);
  }, []);

  useEffect(() => {
    if (pluginData.enterpriseConnectors.length > 0 && registry.length > 0) {
      const _connectors = pluginData.enterpriseConnectors
        .filter((name) => name.includes(type))
        .map((name) => {
          const _name = name.replace(`${type}-`, "");

          const info = registry.find(
            (c) =>
              c.name_oss?.includes(_name) ||
              c.name_cloud?.includes(_name) ||
              c.documentationUrl_oss?.includes(_name) ||
              c.documentationUrl_cloud?.includes(_name),
          );
          return info;
        })
        .filter(Boolean);
      setEnterpriseConnectors(_connectors);
    }
  }, [registry, pluginData]);

  if (registry.length === 0) return <div>{`Loading ${type}s...`}</div>;

  const connectors = registry
    .filter((c) => c.connector_type === type)
    .filter((c) => c.name_oss)
    .filter((c) => c.supportLevel_oss); // at least one connector is missing a support level

  return (
    <Tabs>
      <TabItem value="certified" label="Airbyte Connectors" default>
        <ConnectorTable
          connectors={connectors}
          connectorSupportLevel={"certified"}
        />
      </TabItem>
      <TabItem value="community" label="Marketplace" default>
        <ConnectorTable
          connectors={connectors}
          connectorSupportLevel={"community"}
        />
      </TabItem>
      <TabItem value="enterprise" label="Enterprise" default>
        <ConnectorTable
          connectors={enterpriseConnectors}
          connectorSupportLevel={"enterprise"}
        />
      </TabItem>
      {/* There are no archived connectors to show at the moment, so hiding for now */}
      {/* <TabItem value="archived" label="Archived" default>
        <ConnectorTable
          connectors={connectors}
          connectorSupportLevel={"archived"}
        />
      </TabItem> */}
    </Tabs>
  );
}
