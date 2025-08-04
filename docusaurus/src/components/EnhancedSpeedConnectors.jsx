import React, { useEffect, useState } from "react";
import { REGISTRY_URL } from "../connector_registry";
import styles from "./ConnectorRegistry.module.css";

const iconStyle = { maxWidth: 25, maxHeight: 25 };

const ENHANCED_SPEED_CONNECTORS = {
  source: ["MySQL"],
  destination: ["S3 Data Lake"]
};

async function fetchCatalog(url, setter) {
  const response = await fetch(url);
  const registry = await response.json();
  setter(registry);
}

function connectorSort(a, b) {
  if (a.name_oss < b.name_oss) return -1;
  if (a.name_oss > b.name_oss) return 1;
  return 0;
}

function EnhancedSpeedConnectorList({ registry, type }) {
  const enhancedSpeedNames = ENHANCED_SPEED_CONNECTORS[type] || [];
  
  const filteredConnectors = registry
    .filter((c) => c.connector_type === type)
    .filter((c) => c.name_oss)
    .filter((c) => enhancedSpeedNames.includes(c.name_oss))
    .sort(connectorSort);

  if (filteredConnectors.length === 0) {
    return <p>No {type}s currently support enhanced speed.</p>;
  }

  return (
    <ul>
      {filteredConnectors.map((connector) => {
        const docsLink = connector.documentationUrl_oss?.replace(
          "https://docs.airbyte.com",
          "",
        );
        return (
          <li key={connector.definitionId}>
            <a href={docsLink}>{connector.name_oss}</a>
          </li>
        );
      })}
    </ul>
  );
}

export default function EnhancedSpeedConnectors({ type }) {
  const [registry, setRegistry] = useState([]);

  useEffect(() => {
    fetchCatalog(REGISTRY_URL, setRegistry);
  }, []);

  if (registry.length === 0) return <div>Loading connectors...</div>;

  return <EnhancedSpeedConnectorList registry={registry} type={type} />;
}
