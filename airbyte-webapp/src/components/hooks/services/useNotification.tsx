import { useFetcher, useResource } from "rest-hooks";
import config from "config";
import { useMemo } from "react";

import SourceDefinitionResource from "../../../core/resources/SourceDefinition";
import DestinationDefinitionResource from "../../../core/resources/DestinationDefinition";

type NotificationService = {
  hasNewVersions: boolean;
  hasNewSourceVersion: boolean;
  hasNewDestinationVersion: boolean;
  updateAllSourceVersions: () => void;
  updateAllDestinationVersions: () => void;
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

  const updateSourceDefinition = useFetcher(
    SourceDefinitionResource.updateShape()
  );

  const updateDestinationDefinition = useFetcher(
    DestinationDefinitionResource.updateShape()
  );

  const hasNewSourceVersion = useMemo(
    () =>
      sourceDefinitions.some(
        (source) => source.latestDockerImageTag !== source.dockerImageTag
      ),
    [sourceDefinitions]
  );

  const hasNewDestinationVersion = useMemo(
    () =>
      destinationDefinitions.some(
        (destination) =>
          destination.latestDockerImageTag !== destination.dockerImageTag
      ),
    [destinationDefinitions]
  );

  const hasNewVersions = useMemo(
    () => hasNewSourceVersion || hasNewDestinationVersion,
    [hasNewSourceVersion, hasNewDestinationVersion]
  );

  const updateAllSourceVersions = async () => {
    const updateList = sourceDefinitions.filter(
      (source) => source.latestDockerImageTag !== source.dockerImageTag
    );

    await Promise.all(
      updateList?.map((item) =>
        updateSourceDefinition(
          {},
          {
            sourceDefinitionId: item.sourceDefinitionId,
            dockerImageTag: item.latestDockerImageTag,
          }
        )
      )
    );
  };

  const updateAllDestinationVersions = async () => {
    const updateList = destinationDefinitions.filter(
      (destination) =>
        destination.latestDockerImageTag !== destination.dockerImageTag
    );

    await Promise.all(
      updateList?.map((item) =>
        updateDestinationDefinition(
          {},
          {
            destinationDefinitionId: item.destinationDefinitionId,
            dockerImageTag: item.latestDockerImageTag,
          }
        )
      )
    );
  };

  return {
    hasNewVersions,
    hasNewSourceVersion,
    hasNewDestinationVersion,
    updateAllSourceVersions,
    updateAllDestinationVersions,
  };
};

export default useNotification;
