import { useResource } from "rest-hooks";
import config from "config";

import SourceDefinitionResource from "../../../core/resources/SourceDefinition";
import DestinationDefinitionResource from "../../../core/resources/DestinationDefinition";

type NotificationService = {
  hasNewVersions: () => boolean;
};

const useNotification = (): NotificationService => {
  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );

  const hasNewVersions = () => {
    const hasNewSouceVersion = sourceDefinitions.find(
      (source) => source.latestDockerImageTag !== source.dockerImageTag
    );

    return (
      !!hasNewSouceVersion ||
      !!destinationDefinitions.find(
        (destination) =>
          destination.latestDockerImageTag !== destination.dockerImageTag
      )
    );
  };

  return {
    hasNewVersions,
  };
};

export default useNotification;
