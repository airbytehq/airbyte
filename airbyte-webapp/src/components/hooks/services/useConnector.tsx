import { useFetcher, useResource } from "rest-hooks";
import config from "config";
import { useMemo } from "react";

import SourceDefinitionResource, {
  SourceDefinition,
} from "core/resources/SourceDefinition";
import DestinationDefinitionResource, {
  DestinationDefinition,
} from "core/resources/DestinationDefinition";
import { isConnectorDeprecated } from "core/domain/connector";

type ConnectorService = {
  hasNewVersions: boolean;
  hasNewSourceVersion: boolean;
  hasNewDestinationVersion: boolean;
  countNewSourceVersion: number;
  countNewDestinationVersion: number;
  updateAllSourceVersions: () => void;
  updateAllDestinationVersions: () => void;
};

function hasLatestVersion(
  connector: SourceDefinition | DestinationDefinition
): boolean {
  return (
    !isConnectorDeprecated(connector) &&
    connector.latestDockerImageTag !== connector.dockerImageTag
  );
}

const useConnector = (): ConnectorService => {
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
    () => sourceDefinitions.some(hasLatestVersion),
    [sourceDefinitions]
  );

  const hasNewDestinationVersion = useMemo(
    () => destinationDefinitions.some(hasLatestVersion),
    [destinationDefinitions]
  );

  const hasNewVersions = hasNewSourceVersion || hasNewDestinationVersion;

  const newSourceDefinitions = useMemo(
    () => sourceDefinitions.filter(hasLatestVersion),
    [sourceDefinitions]
  );

  const newDestinationDefinitions = useMemo(
    () => destinationDefinitions.filter(hasLatestVersion),
    [destinationDefinitions]
  );

  const updateAllSourceVersions = async () => {
    await Promise.all(
      newSourceDefinitions?.map((item) =>
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
    await Promise.all(
      newDestinationDefinitions?.map((item) =>
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
    countNewSourceVersion: newSourceDefinitions.length,
    countNewDestinationVersion: newDestinationDefinitions.length,
  };
};

export default useConnector;
