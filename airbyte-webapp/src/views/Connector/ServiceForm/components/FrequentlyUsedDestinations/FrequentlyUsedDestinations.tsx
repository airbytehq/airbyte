import React, { useMemo } from "react";

import { ConnectorDefinition } from "core/domain/connector";
import { isDestinationDefinition } from "core/domain/connector/destination";
import { useExperiment } from "hooks/services/Experiment";
import { DestinationDefinitionReadWithLatestTag } from "services/connector/DestinationDefinitionService";

import { DestinationConnectorCard } from "../../types";
import { FrequentlyUsedDestinationsCard } from "./FrequentlyUsedDestinationsCard";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";

interface FrequentlyUsedDestinationsProps {
  availableServices: ConnectorDefinition[];
  onDestinationSelect: (id: string) => void;
}

export const FrequentlyUsedDestinations: React.FC<FrequentlyUsedDestinationsProps> = ({
  availableServices,
  onDestinationSelect,
}) => {
  const frequentlyUsedDestinationIds = useExperiment("connector.frequentlyUsedDestinationIds", [
    "22f6c74f-5699-40ff-833c-4a879ea40133",
    "424892c4-daac-4491-b35d-c6688ba547ba",
  ]);
  const { trackSelectedSuggestedDestination } = useAnalyticsTrackFunctions();

  const frequentlyUsedDestinations: DestinationConnectorCard[] = useMemo(
    () =>
      availableServices
        .filter(
          (service): service is DestinationDefinitionReadWithLatestTag =>
            isDestinationDefinition(service) && frequentlyUsedDestinationIds.includes(service.destinationDefinitionId)
        )
        .map(({ destinationDefinitionId, name, icon, releaseStage }) => ({
          destinationDefinitionId,
          name,
          icon,
          releaseStage,
        })),
    [availableServices, frequentlyUsedDestinationIds]
  );

  const onDestinationCardClick = (id: string, connectorName: string) => {
    onDestinationSelect(id);
    trackSelectedSuggestedDestination(id, connectorName);
  };

  return (
    <FrequentlyUsedDestinationsCard
      destinations={frequentlyUsedDestinations}
      onDestinationSelect={onDestinationCardClick}
    />
  );
};
