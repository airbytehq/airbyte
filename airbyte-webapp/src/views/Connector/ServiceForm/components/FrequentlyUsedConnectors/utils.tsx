import { Connector, ConnectorDefinition } from "core/domain/connector";
import { ReleaseStage } from "core/request/AirbyteClient";

export interface FrequentlyUsedConnectorProps {
  id: string;
  name: string;
  icon?: string;
  releaseStage?: ReleaseStage;
}

const transformConnectorDefinitionToFrequentlyUsedConnector = (
  item: ConnectorDefinition
): FrequentlyUsedConnectorProps => ({
  id: Connector.id(item),
  name: item.name,
  icon: item.icon,
  releaseStage: item.releaseStage,
});

const sortUsingOrderOverwrite =
  (featuredConnectorIds: string[]) => (a: FrequentlyUsedConnectorProps, b: FrequentlyUsedConnectorProps) => {
    return Number(featuredConnectorIds.includes(b.id)) - Number(featuredConnectorIds.includes(a.id));
  };

export const getSortedFrequentlyUsedDataUsingExperiment = (
  availableConnectorDefinitions: ConnectorDefinition[],
  featuredConnectorIds: string[]
) =>
  availableConnectorDefinitions
    .map(transformConnectorDefinitionToFrequentlyUsedConnector)
    .sort(sortUsingOrderOverwrite(featuredConnectorIds));
