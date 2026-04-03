import TabItem from "@theme/TabItem";
import Tabs from "@theme/Tabs";
import styles from "./ConnectorRegistry.module.css";

const iconStyle = { maxWidth: 25, maxHeight: 25 };

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

function ConnectorTable({ connectors, connectorSupportLevel, enterpriseConnectors = [] }) {
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
          .filter((c) => {
            if (connectorSupportLevel === "enterprise") {
              return true;
            }
            
            const isEnterpriseConnector = enterpriseConnectors.some(
              ec => ec && c && (ec.definitionId === c.definitionId || ec.name_oss === c.name_oss)
            );
            
            return !isEnterpriseConnector && c.supportLevel_oss === connectorSupportLevel;
          })
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

export default function ConnectorRegistry({ type, connectorsJSON, enterpriseConnectorsJSON }) {
  const connectors = JSON.parse(connectorsJSON);
  const enterpriseConnectors = JSON.parse(enterpriseConnectorsJSON);

  return (
    <Tabs>
      <TabItem value="certified" label="Airbyte Connectors" default>
        <ConnectorTable
          connectors={connectors}
          connectorSupportLevel={"certified"}
          enterpriseConnectors={enterpriseConnectors}
        />
      </TabItem>
      <TabItem value="community" label="Marketplace" default>
        <ConnectorTable
          connectors={connectors}
          connectorSupportLevel={"community"}
          enterpriseConnectors={enterpriseConnectors}
        />
      </TabItem>
      <TabItem value="enterprise" label="Enterprise" default>
        <ConnectorTable
          connectors={enterpriseConnectors}
          connectorSupportLevel={"enterprise"}
          enterpriseConnectors={enterpriseConnectors}
        />
      </TabItem>
    </Tabs>
  );
}
