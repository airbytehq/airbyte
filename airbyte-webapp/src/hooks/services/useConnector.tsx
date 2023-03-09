import { useMemo } from "react";
import { useMutation } from "react-query";

import { useConfig } from "config";
import { ConnectionConfiguration } from "core/domain/connection";
import { Connector } from "core/domain/connector";
import { DestinationService } from "core/domain/connector/DestinationService";
import { SourceService } from "core/domain/connector/SourceService";
import { useGetOutOfDateConnectorsCount } from "services/connector/ConnectorDefinitions";
import {
  useDestinationDefinitionList,
  useUpdateDestinationDefinition,
} from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList, useUpdateSourceDefinition } from "services/connector/SourceDefinitionService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

import { CheckConnectionRead } from "../../core/request/AirbyteClient";

export const useUpdateSourceDefinitions = () => {
  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: updateSourceDefinition } = useUpdateSourceDefinition();

  const newSourceDefinitions = useMemo(() => sourceDefinitions.filter(Connector.hasNewerVersion), [sourceDefinitions]);

  const updateAllSourceVersions = async () => {
    await Promise.all(
      newSourceDefinitions?.map((item) =>
        updateSourceDefinition({
          sourceDefinitionId: item.sourceDefinitionId,
          dockerImageTag: item.latestDockerImageTag ?? "",
        })
      )
    );
  };

  return { updateAllSourceVersions };
};

export const useUpdateDestinationDefinitions = () => {
  const { destinationDefinitions } = useDestinationDefinitionList();
  const { mutateAsync: updateDestinationDefinition } = useUpdateDestinationDefinition();

  const newDestinationDefinitions = useMemo(
    () => destinationDefinitions.filter(Connector.hasNewerVersion),
    [destinationDefinitions]
  );

  const updateAllDestinationVersions = async () => {
    await Promise.all(
      newDestinationDefinitions?.map((item) =>
        updateDestinationDefinition({
          destinationDefinitionId: item.destinationDefinitionId,
          dockerImageTag: item.latestDockerImageTag ?? "",
        })
      )
    );
  };

  return { updateAllDestinationVersions };
};

export const useGetConnectorsOutOfDate = () => {
  const outOfDateConnectors = useGetOutOfDateConnectorsCount();

  const hasNewSourceVersion = outOfDateConnectors.sourceDefinitions > 0;
  const hasNewDestinationVersion = outOfDateConnectors.destinationDefinitions > 0;
  const hasNewVersions = hasNewSourceVersion || hasNewDestinationVersion;

  return {
    hasNewVersions,
    hasNewSourceVersion,
    hasNewDestinationVersion,
    countNewSourceVersion: outOfDateConnectors.sourceDefinitions,
    countNewDestinationVersion: outOfDateConnectors.destinationDefinitions,
    outOfDateConnectors,
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

export type CheckConnectorParams = { signal: AbortSignal } & (
  | { selectedConnectorId: string }
  | {
      selectedConnectorId: string;
      name: string;
      connectionConfiguration: ConnectionConfiguration;
    }
  | {
      selectedConnectorDefinitionId: string;
      connectionConfiguration: ConnectionConfiguration;
      workspaceId: string;
    }
);

export const useCheckConnector = (formType: "source" | "destination") => {
  const destinationService = useGetDestinationService();
  const sourceService = useGetSourceService();

  return useMutation<CheckConnectionRead, Error, CheckConnectorParams>(async (params: CheckConnectorParams) => {
    const payload: Record<string, unknown> = {};

    if ("connectionConfiguration" in params) {
      payload.connectionConfiguration = params.connectionConfiguration;
    }

    if ("name" in params) {
      payload.name = params.name;
    }

    if ("workspaceId" in params) {
      payload.workspaceId = params.workspaceId;
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
