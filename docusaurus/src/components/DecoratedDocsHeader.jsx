import React from "react";
import { useEffect, useState } from "react";

const registry_url =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

export function DecoratedDocsHeader({ name }) {
  const [connector, setConnector] = useState(null);

  useEffect(() => {
    fetchCatalog(registry_url, name, setConnector);
  }, []);

  if (!connector) return null;

  return (
    <div>
      <small>
        <table>
          <tbody>
            <tr>
              <td rowSpan={3}>
                <img style={{ maxHeight: 75 }} src={connector.iconUrl_oss} />
              </td>
              <td>Support Level: </td>
              <td>{connector.supportLevel_oss}</td>
            </tr>
            <tr>
              <td>Definition Id: </td>
              <td>{connector.definitionId}</td>
            </tr>
            <tr>
              <td> Latest Version: </td>
              <td>{connector.dockerImageTag_oss}</td>
            </tr>
          </tbody>
        </table>
      </small>
      <br /> <br />
    </div>
  );
}

async function fetchCatalog(url, name, setter) {
  const response = await fetch(url);
  const registry = await response.json();
  const connector = registry.find(
    (c) => c.dockerRepository_oss === `airbyte/${name}`
  );
  setter(connector);
}
