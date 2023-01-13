import { ReleaseStage, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useExperiment } from "hooks/services/Experiment";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

export const useFreeConnectorProgram = () => {
  const isFreeConnectorProgramEnabled = useExperiment("workspace.freeConnectorsProgram.visible", false);

  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  // todo: implement actual call once it is merged with issue #4006
  // for now, we'll just default to false for enrolled
  const enrolledInFreeConnectorProgram = false;

  const showEnrollmentContent = !enrolledInFreeConnectorProgram && isFreeConnectorProgramEnabled;

  const connectionHasAlphaOrBetaConnector = (connection: WebBackendConnectionRead) => {
    if (!isFreeConnectorProgramEnabled) {
      return null;
    }

    return (
      sourceDefinitions.find((source) => source.sourceDefinitionId === connection.source.sourceDefinitionId)
        ?.releaseStage === (ReleaseStage.alpha || ReleaseStage.beta) ||
      destinationDefinitions.find(
        (destination) => destination.destinationDefinitionId === connection.destination.destinationDefinitionId
      )?.releaseStage === (ReleaseStage.alpha || ReleaseStage.beta)
    );
  };

  return { isFreeConnectorProgramEnabled, showEnrollmentContent, connectionHasAlphaOrBetaConnector };
};
