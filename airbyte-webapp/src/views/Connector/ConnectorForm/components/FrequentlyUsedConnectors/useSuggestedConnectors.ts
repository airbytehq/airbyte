import { useMemo } from "react";

import { ConnectorDefinition } from "core/domain/connector";
import { isDestinationDefinition } from "core/domain/connector/destination";
import { isSourceDefinition } from "core/domain/connector/source";

import { SuggestedConnector } from "../../types";

interface useSuggestedConnectorsProps {
  availableServices: ConnectorDefinition[];
  connectorIds: string[];
}
export const useSuggestedConnectors = ({
  availableServices,
  connectorIds,
}: useSuggestedConnectorsProps): SuggestedConnector[] => {
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
              connectorDefinitionId: destinationDefinitionId,
              name,
              icon,
              releaseStage,
            };
          }

          const { sourceDefinitionId, name, icon, releaseStage } = service;
          return {
            connectorDefinitionId: sourceDefinitionId,
            name,
            icon,
            releaseStage,
          };
        }),
    [availableServices, connectorIds]
  );
};
