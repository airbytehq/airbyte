import { usePluginData } from "@docusaurus/useGlobalData";
import TabItem from "@theme/TabItem";
import Tabs from "@theme/Tabs";
import { useEffect, useState } from "react";
import { COMPOSITE_REGISTRY_URL } from "../constants";
import styles from "./ConnectorRegistry.module.css";

const iconStyle = { maxWidth: 25, maxHeight: 25 };

const GITHUB_REPO_NAME = "airbytehq/airbyte";
const CONNECTORS_PATH = "airbyte-integrations/connectors";

function buildCompositeEntry(entry, connectorType) {
  const dockerRepository = entry.dockerRepository || "";
  const connectorName = dockerRepository.replace("airbyte/", "");
  const definitionId =
    entry.sourceDefinitionId || entry.destinationDefinitionId || "";
  const availability = entry.availability || [];

  const githubUrl = `https://github.com/${GITHUB_REPO_NAME}/blob/master/${CONNECTORS_PATH}/${connectorName}`;
  const issuesLabel = `connectors/${connectorType}/${connectorName.replace(`${connectorType}-`, "")}`;
  const issueUrl = `https://github.com/${GITHUB_REPO_NAME}/issues?q=is:open+is:issue+label:${issuesLabel}`;

  return {
    connector_type: connectorType,
    definitionId,
    is_oss: availability.includes("oss"),
    is_cloud: availability.includes("cloud"),
    github_url: githubUrl,
    issue_url: issueUrl,

    name: entry.name || "",
    dockerRepository,
    dockerImageTag: entry.dockerImageTag || "",
    supportLevel: entry.supportLevel || "community",
    iconUrl: entry.iconUrl || "",
    documentationUrl: entry.documentationUrl || "",
  };
}

async function fetchCatalog(setter) {
  try {
    const response = await fetch(COMPOSITE_REGISTRY_URL);
    if (!response.ok) {
      throw new Error(
        `Failed to fetch composite registry: ${response.statusText}`,
      );
    }
    const compositeRegistry = await response.json();
    const sources = compositeRegistry.sources || [];
    const destinations = compositeRegistry.destinations || [];
    setter([
      ...sources.map((entry) => buildCompositeEntry(entry, "source")),
      ...destinations.map((entry) => buildCompositeEntry(entry, "destination")),
    ]);
  } catch (error) {
    console.error("Failed to fetch connector registry:", error);
    setter([]);
  }
}

/*
Sorts connectors by release stage and then name
*/
function connectorSort(a, b) {
  if (a.supportLevel !== b.supportLevel) {
    if (a.supportLevel === "certified") return -3;
    if (b.supportLevel === "certified") return 3;
    if (a.supportLevel === "community") return -2;
    if (b.supportLevel === "community") return 2;
    if (a.supportLevel === "archived") return -1;
    if (b.supportLevel === "archived") return 1;
  }

  if (a.name < b.name) return -1;
  if (a.name > b.name) return 1;
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
              ec => ec && c && (ec.definitionId === c.definitionId || ec.name === c.name)
            );
            
            return !isEnterpriseConnector && c.supportLevel === connectorSupportLevel;
          })
          .map((connector) => {
            const docsLink = connector.documentationUrl?.replace(
              "https://docs.airbyte.com",
              "",
            ); // not using documentationUrl so we can have relative links

            return (
              <tr key={`${connector.definitionId}`}>
                <td>
                  <div className={styles.connectorName}>
                    {connector.iconUrl && (
                      <div className={styles.connectorIconBackground}>
                        <img src={connector.iconUrl} style={iconStyle} />
                      </div>
                    )}

                    <a href={docsLink}>{connector.name}</a>
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
                    {connector.supportLevel != "archived" &&
                    connector.github_url  ? (
                      <a href={connector.github_url}>⚙️</a>
                    ) : (
                      ""
                    )}
                    {connector.supportLevel != "archived" ? (
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
                        {connector.dockerRepository}:
                      {connector.dockerImageTag}
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
  // `null` = loading, `[]` = fetch failed / empty, populated array = loaded.
  const [registry, setRegistry] = useState(null);
  const [enterpriseConnectors, setEnterpriseConnectors] = useState([]);

  useEffect(() => {
    fetchCatalog(setRegistry);
  }, []);

  useEffect(() => {
    if (registry && registry.length > 0) {
      const enterpriseFromRegistry = registry.filter(
        (c) =>
          c.connector_type === type &&
          c.documentationUrl?.includes("/integrations/enterprise-connectors/"),
      );

      const enterpriseFromPlugin = pluginData.enterpriseConnectors.length > 0
        ? pluginData.enterpriseConnectors
            .filter((name) => name.includes(type))
            .map((name) => {
              const _name = name.replace(`${type}-`, "");

              const info = registry.find(
                (c) =>
                  c.name?.includes(_name) ||
                  c.documentationUrl?.includes(_name),
              );
              return info;
            })
            .filter(Boolean)
        : [];

      const allEnterpriseConnectors = [...enterpriseFromRegistry, ...enterpriseFromPlugin];
      const uniqueEnterpriseConnectors = Array.from(
        new Map(allEnterpriseConnectors.map(c => [c.definitionId, c])).values()
      );

      setEnterpriseConnectors(uniqueEnterpriseConnectors);
    }
  }, [registry, pluginData, type]);

  if (registry === null) return <div>{`Loading ${type}s...`}</div>;
  if (registry.length === 0)
    return <div>{`Failed to load ${type}s. Check your network connection and try again.`}</div>;

  const connectors = registry
    .filter((c) => c.connector_type === type)
    .filter((c) => c.name)
    .filter((c) => c.supportLevel); // at least one connector is missing a support level

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
