import { WebBackendConnectionListItem, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

import { useFreeConnectorProgram } from "./useFreeConnectorProgram";
import { freeReleaseStages } from "../lib/model";

/**
 * Detects whether a given connection is free according to the terms of the free connector program.
 * A connection might be disabled in the UI due to a negative credit balance, but we still want to enable it
 * if the user is enrolled in the FCP and the connection is eligible.
 */
export const useIsConnectionFree = (connection: WebBackendConnectionRead | WebBackendConnectionListItem): boolean => {
  const { userDidEnroll } = useFreeConnectorProgram();
  const sourceReleaseStage = useSourceDefinition(connection.source.sourceDefinitionId).releaseStage;
  const destinationReleaseStage = useDestinationDefinition(connection.destination.destinationDefinitionId).releaseStage;
  const isSourceEligible = sourceReleaseStage && freeReleaseStages.includes(sourceReleaseStage);
  const isDestinationEligible = destinationReleaseStage && freeReleaseStages.includes(destinationReleaseStage);

  return Boolean(userDidEnroll && (isSourceEligible || isDestinationEligible));
};
