import { useFetcher } from "rest-hooks";
import { useMemo } from "react";

import SourceDefinitionResource from "core/resources/SourceDefinition";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import { Connector } from "core/domain/connector";
import { useSourceDefinitionList } from "./useSourceDefinition";
import { useDestinationDefinitionList } from "./useDestinationDefinition";

type ConnectorService = {
  hasNewVersions: boolean;
  hasNewSourceVersion: boolean;
  hasNewDestinationVersion: boolean;
  countNewSourceVersion: number;
  countNewDestinationVersion: number;
  updateAllSourceVersions: () => void;
  updateAllDestinationVersions: () => void;
};

const useConnector = (): ConnectorService => {
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const updateSourceDefinition = useFetcher(
    SourceDefinitionResource.updateShape()
  );
  const updateDestinationDefinition = useFetcher(
    DestinationDefinitionResource.updateShape()
  );

  const newSourceDefinitions = useMemo(
    () => sourceDefinitions.filter(Connector.hasNewerVersion),
    [sourceDefinitions]
  );

  const newDestinationDefinitions = useMemo(
    () => destinationDefinitions.filter(Connector.hasNewerVersion),
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

  const hasNewSourceVersion = newSourceDefinitions.length > 0;
  const hasNewDestinationVersion = newDestinationDefinitions.length > 0;
  const hasNewVersions = hasNewSourceVersion || hasNewDestinationVersion;

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
