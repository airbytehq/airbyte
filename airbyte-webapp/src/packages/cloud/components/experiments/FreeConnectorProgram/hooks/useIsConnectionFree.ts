import { WebBackendConnectionListItem, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

import { useFreeConnectorProgram } from "./useFreeConnectorProgram";
import { freeReleaseStages } from "../lib/model";

export const useIsConnectionFree = (connection: WebBackendConnectionRead | WebBackendConnectionListItem): boolean => {
  const { userDidEnroll } = useFreeConnectorProgram();
  const sourceReleaseStage = useSourceDefinition(connection.source.sourceDefinitionId).releaseStage;
  const destinationReleaseStage = useDestinationDefinition(connection.destination.destinationDefinitionId).releaseStage;
  const isSourceEligible = sourceReleaseStage && freeReleaseStages.includes(sourceReleaseStage);
  const isDestinationEligible = destinationReleaseStage && freeReleaseStages.includes(destinationReleaseStage);

  return Boolean(userDidEnroll && (isSourceEligible || isDestinationEligible));
};
