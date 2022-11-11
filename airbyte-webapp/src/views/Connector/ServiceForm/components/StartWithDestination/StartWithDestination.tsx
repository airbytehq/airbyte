import React, { useMemo } from "react";

import { ConnectorDefinition } from "core/domain/connector";
import { isDestinationDefinition } from "core/domain/connector/destination";
import { useExperiment } from "hooks/services/Experiment";
import { DestinationDefinitionReadWithLatestTag } from "services/connector/DestinationDefinitionService";

import { DestinationConnectorCard } from "../../types";
import { StartWithDestinationCard } from "./StartWithDestinationCard";

interface StartWithDestinationProps {
  onDestinationSelect: (id: string) => void;
  availableServices: ConnectorDefinition[];
}

export const StartWithDestination: React.FC<StartWithDestinationProps> = ({
  onDestinationSelect,
  availableServices,
}) => {
  const startWithDestinationId = useExperiment("connector.startWithDestinationId", "");

  const startWithDestination = useMemo<DestinationConnectorCard | undefined>(() => {
    const destination = availableServices.find(
      (service): service is DestinationDefinitionReadWithLatestTag =>
        isDestinationDefinition(service) && service.destinationDefinitionId === startWithDestinationId
    );
    if (!destination) {
      return undefined;
    }
    const { destinationDefinitionId, name, icon, releaseStage } = destination;

    return { destinationDefinitionId, name, icon, releaseStage };
  }, [availableServices, startWithDestinationId]);

  return <StartWithDestinationCard onDestinationSelect={onDestinationSelect} destination={startWithDestination} />;
};
