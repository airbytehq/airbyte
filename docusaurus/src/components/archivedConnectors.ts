export type ArchivedConnector = {
  connectorName: string;
  name_oss: string;
  dockerRepository_oss: string;
  definitionId: string;
  is_oss: false;
  is_cloud: false;
  iconUrl_oss: string;
  supportLevel_oss: string;
  documentationUrl_oss: string;
};

type BaseArchivedConnector = {
  name: string;
  type: "source" | "destination";
  definitionId: string;
};

const baseArchivedConnectors: BaseArchivedConnector[] = [
  {
    name: "KVdb",
    type: "destination",
    definitionId: "f2e549cd-8e2a-48f8-822d-cc13630eb42d",
  },
];

export const archivedConnectors: ArchivedConnector[] =
  baseArchivedConnectors.map((archivedConnector) => {
    const dockerName = `${
      archivedConnector.type
    }-${archivedConnector.name.toLowerCase()}`;

    const connector: ArchivedConnector = {
      name_oss: dockerName,
      connectorName: archivedConnector.name,
      dockerRepository_oss: `airbyte/${dockerName}`,
      definitionId: archivedConnector.definitionId,
      is_oss: false,
      is_cloud: false,
      iconUrl_oss: `https://connectors.airbyte.com/files/metadata/airbyte/${dockerName}/latest/icon.svg`,
      supportLevel_oss: "archived",
      documentationUrl_oss: `https://docs.airbyte.com/integrations/${
        archivedConnector.type
      }s/${archivedConnector.name.toLowerCase()}`,
    };

    return connector;
  });
