import { useResource } from "rest-hooks";
import config from "config";
import { useMemo } from "react";

import SourceDefinitionResource from "../../../core/resources/SourceDefinition";
import DestinationDefinitionResource from "../../../core/resources/DestinationDefinition";

type NotificationService = {
  hasNewVersions: boolean;
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

  const hasNewVersions = useMemo(() => {
    const hasNewSourceVersion = sourceDefinitions.some(
      (source) => source.latestDockerImageTag !== source.dockerImageTag
    );

    const hasNewDestinationVersion = destinationDefinitions.some(
      (destination) =>
        destination.latestDockerImageTag !== destination.dockerImageTag
    );

    return hasNewSourceVersion || hasNewDestinationVersion;
  }, [sourceDefinitions, destinationDefinitions]);

  return {
    hasNewVersions,
  };
};

export default useNotification;
