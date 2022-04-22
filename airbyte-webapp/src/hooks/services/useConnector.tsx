import { useMemo } from "react";
import { useMutation } from "react-query";

import { useConfig } from "config";
import { ConnectionConfiguration } from "core/domain/connection";
import { Connector, Scheduler } from "core/domain/connector";
import { DestinationService } from "core/domain/connector/DestinationService";
import { SourceService } from "core/domain/connector/SourceService";
import {
  useDestinationDefinitionList,
  useUpdateDestinationDefinition,
} from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList, useUpdateSourceDefinition } from "services/connector/SourceDefinitionService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

type ConnectorService = {
  hasNewVersions: boolean;
  hasNewSourceVersion: boolean;
  hasNewDestinationVersion: boolean;
  countNewSourceVersion: number;
  countNewDestinationVersion: number;
  updateAllSourceVersions: () => unknown;
  updateAllDestinationVersions: () => unknown;
};

const useConnector = (): ConnectorService => {
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const { mutateAsync: updateSourceDefinition } = useUpdateSourceDefinition();
  const { mutateAsync: updateDestinationDefinition } = useUpdateDestinationDefinition();

  const newSourceDefinitions = useMemo(() => sourceDefinitions.filter(Connector.hasNewerVersion), [sourceDefinitions]);

  const newDestinationDefinitions = useMemo(
    () => destinationDefinitions.filter(Connector.hasNewerVersion),
    [destinationDefinitions]
  );

  const updateAllSourceVersions = async () => {
    await Promise.all(
      newSourceDefinitions?.map((item) =>
        updateSourceDefinition({
          sourceDefinitionId: item.sourceDefinitionId,
          dockerImageTag: item.latestDockerImageTag,
        })
      )
    );
  };

  const updateAllDestinationVersions = async () => {
    await Promise.all(
      newDestinationDefinitions?.map((item) =>
        updateDestinationDefinition({
          destinationDefinitionId: item.destinationDefinitionId,
          dockerImageTag: item.latestDockerImageTag,
        })
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

function useGetDestinationService(): DestinationService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new DestinationService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}

function useGetSourceService(): SourceService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new SourceService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}

type CheckConnectorParams = { signal: AbortSignal } & (
  | { selectedConnectorId: string }
  | {
      selectedConnectorId: string;
      name: string;
      connectionConfiguration: ConnectionConfiguration;
    }
  | {
      selectedConnectorDefinitionId: string;
      connectionConfiguration: ConnectionConfiguration;
    }
);

const useCheckConnector = (formType: "source" | "destination") => {
  const destinationService = useGetDestinationService();
  const sourceService = useGetSourceService();

  return useMutation<Scheduler, Error, CheckConnectorParams>(async (params: CheckConnectorParams) => {
    const payload: Record<string, unknown> = {};

    if ("connectionConfiguration" in params) {
      payload.connectionConfiguration = params.connectionConfiguration;
    }

    if ("name" in params) {
      payload.name = params.name;
    }

    if (formType === "destination") {
      if ("selectedConnectorId" in params) {
        payload.destinationId = params.selectedConnectorId;
      }

      if ("selectedConnectorDefinitionId" in params) {
        payload.destinationDefinitionId = params.selectedConnectorDefinitionId;
      }

      return await destinationService.check_connection(payload, {
        signal: params.signal,
      });
    }

    if ("selectedConnectorId" in params) {
      payload.sourceId = params.selectedConnectorId;
    }

    if ("selectedConnectorDefinitionId" in params) {
      payload.sourceDefinitionId = params.selectedConnectorDefinitionId;
    }

    return await sourceService.check_connection(payload, {
      signal: params.signal,
    });
  });
};

export { useCheckConnector };
export type { CheckConnectorParams };
export default useConnector;
