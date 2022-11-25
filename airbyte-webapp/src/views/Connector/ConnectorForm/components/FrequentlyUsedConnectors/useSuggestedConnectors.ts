import { useMemo } from "react";

import { ConnectorDefinition } from "core/domain/connector";
import { isDestinationDefinition } from "core/domain/connector/destination";
import { isSourceDefinition } from "core/domain/connector/source";

import { ConnectorCard } from "../../types";

interface Props {
  availableServices: ConnectorDefinition[];
  connectorIds: string[];
}
export const useSuggestedConnectors = ({ availableServices, connectorIds }: Props): ConnectorCard[] => {
  return useMemo(
    () =>
      availableServices
        .filter((service) => {
          if (isDestinationDefinition(service)) {
            return connectorIds.includes(service.destinationDefinitionId);
          }

          return isSourceDefinition(service) && connectorIds.includes(service.sourceDefinitionId);
        })
        .map((service) => {
          if (isDestinationDefinition(service)) {
            const { destinationDefinitionId, name, icon, releaseStage } = service;
            return {
              id: destinationDefinitionId,
              destinationDefinitionId,
              name,
              icon,
              releaseStage,
            };
          }

          const { sourceDefinitionId, name, icon, releaseStage } = service;
          return {
            id: sourceDefinitionId,
            sourceDefinitionId,
            name,
            icon,
            releaseStage,
          };
        }),
    [availableServices, connectorIds]
  );
};
