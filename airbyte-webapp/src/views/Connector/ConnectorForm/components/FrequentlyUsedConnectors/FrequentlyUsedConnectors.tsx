import React from "react";

import { ConnectorDefinition } from "core/domain/connector";

import { FrequentlyUsedConnectorsCard } from "./FrequentlyUsedConnectorsCard";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useSuggestedConnectors } from "./useSuggestedConnectors";

interface FrequentlyUsedConnectorsProps {
  availableServices: ConnectorDefinition[];
  connectorType: "source" | "destination";
  connectorIds: string[];
  onConnectorSelect: (connectorDefinitionId: string) => void;
}

export const FrequentlyUsedConnectors: React.FC<FrequentlyUsedConnectorsProps> = ({
  availableServices,
  connectorType,
  connectorIds,
  onConnectorSelect,
}) => {
  const { trackSelectedSuggestedDestination } = useAnalyticsTrackFunctions();

  const suggestedConnectors = useSuggestedConnectors({ availableServices, connectorIds });
  const onConnectorCardClick = (connectorDefinitionId: string, connectorName: string) => {
    onConnectorSelect(connectorDefinitionId);
    trackSelectedSuggestedDestination(connectorDefinitionId, connectorName);
  };

  return (
    <FrequentlyUsedConnectorsCard
      connectors={suggestedConnectors}
      onConnectorSelect={onConnectorCardClick}
      connectorType={connectorType}
    />
  );
};
