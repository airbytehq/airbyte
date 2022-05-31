import { QueryClient, useMutation, useQueryClient } from "react-query";

import FrequencyConfig from "config/FrequencyConfig.json";
import { SyncSchema } from "core/domain/catalog";
import { WebBackendConnectionService } from "core/domain/connection";
import { ConnectionService } from "core/domain/connection/ConnectionService";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useInitService } from "services/useInitService";
import { equal } from "utils/objects";

import { useConfig } from "../../config";
import {
  ConnectionSchedule,
  DestinationRead,
  NamespaceDefinitionType,
  OperationCreate,
  SourceDefinitionRead,
  SourceRead,
  WebBackendConnectionRead,
  WebBackendConnectionUpdate,
} from "../../core/request/AirbyteClient";
import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";
import { SCOPE_WORKSPACE } from "../../services/Scope";
import { useDefaultRequestMiddlewares } from "../../services/useDefaultRequestMiddlewares";
import { useCurrentWorkspace } from "./useWorkspace";

export const connectionsKeys = {
  all: [SCOPE_WORKSPACE, "connections"] as const,
  lists: () => [...connectionsKeys.all, "list"] as const,
  list: (filters: string) => [...connectionsKeys.lists(), { filters }] as const,
  detail: (connectionId: string) => [...connectionsKeys.all, "details", connectionId] as const,
};

export type ValuesProps = {
  name?: string;
  schedule: ConnectionSchedule | null;
  prefix: string;
  syncCatalog: SyncSchema;
  namespaceDefinition: NamespaceDefinitionType;
  namespaceFormat?: string;
  operations?: OperationCreate[];
};

type CreateConnectionProps = {
  values: ValuesProps;
  source: SourceRead;
  destination: DestinationRead;
  sourceDefinition?: Pick<SourceDefinitionRead, "sourceDefinitionId">;
  destinationDefinition?: { name: string; destinationDefinitionId: string };
  sourceCatalogId: string | undefined;
};

export type ListConnection = { connections: WebBackendConnectionRead[] };

function useWebConnectionService() {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(
    () => new WebBackendConnectionService(config.apiUrl, middlewares),
    [config.apiUrl, middlewares]
  );
}

function useConnectionService() {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(() => new ConnectionService(config.apiUrl, middlewares), [config.apiUrl, middlewares]);
}

export const useConnectionLoad = (
  connectionId: string
): {
  connection: WebBackendConnectionRead;
  refreshConnectionCatalog: () => Promise<WebBackendConnectionRead>;
} => {
  const connection = useGetConnection(connectionId);
  const connectionService = useWebConnectionService();

  const refreshConnectionCatalog = async () => await connectionService.getConnection(connectionId, true);

  return {
    connection,
    refreshConnectionCatalog,
  };
};

export const useSyncConnection = () => {
  const service = useConnectionService();
  const analyticsService = useAnalyticsService();

  return useMutation((connection: WebBackendConnectionRead) => {
    const frequency = FrequencyConfig.find((item) => equal(item.config, connection.schedule));

    analyticsService.track("Source - Action", {
      action: "Full refresh sync",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: frequency?.text,
    });

    return service.sync(connection.connectionId);
  });
};

export const useResetConnection = () => {
  const service = useConnectionService();

  return useMutation((connectionId: string) => service.reset(connectionId));
};

const useGetConnection = (connectionId: string, options?: { refetchInterval: number }): WebBackendConnectionRead => {
  const service = useWebConnectionService();

  return useSuspenseQuery(connectionsKeys.detail(connectionId), () => service.getConnection(connectionId), options);
};

const useCreateConnection = () => {
  const service = useWebConnectionService();
  const queryClient = useQueryClient();
  const analyticsService = useAnalyticsService();

  return useMutation(
    async ({
      values,
      source,
      destination,
      sourceDefinition,
      destinationDefinition,
      sourceCatalogId,
    }: CreateConnectionProps) => {
      const response = await service.create({
        sourceId: source.sourceId,
        destinationId: destination.destinationId,
        ...values,
        status: "active",
        sourceCatalogId,
      });

      const enabledStreams = values.syncCatalog.streams.filter((stream) => stream.config?.selected).length;

      const frequencyData = FrequencyConfig.find((item) => equal(item.config, values.schedule));

      analyticsService.track("New Connection - Action", {
        action: "Set up connection",
        frequency: frequencyData?.text,
        connector_source_definition: source?.sourceName,
        connector_source_definition_id: sourceDefinition?.sourceDefinitionId,
        connector_destination_definition: destination?.destinationName,
        connector_destination_definition_id: destinationDefinition?.destinationDefinitionId,
        available_streams: values.syncCatalog.streams.length,
        enabled_streams: enabledStreams,
      });

      return response;
    },
    {
      onSuccess: (data) => {
        queryClient.setQueryData(connectionsKeys.lists(), (lst: ListConnection | undefined) => ({
          connections: [data, ...(lst?.connections ?? [])],
        }));
      },
    }
  );
};

const useDeleteConnection = () => {
  const service = useConnectionService();
  const queryClient = useQueryClient();

  return useMutation((connectionId: string) => service.delete(connectionId), {
    onSuccess: (_data, connectionId) => {
      queryClient.removeQueries(connectionsKeys.detail(connectionId));
      queryClient.setQueryData(
        connectionsKeys.lists(),
        (lst: ListConnection | undefined) =>
          ({
            connections: lst?.connections.filter((conn) => conn.connectionId !== connectionId) ?? [],
          } as ListConnection)
      );
    },
  });
};

const useUpdateConnection = () => {
  const service = useWebConnectionService();
  const queryClient = useQueryClient();

  return useMutation(
    (conn: WebBackendConnectionUpdate) => {
      const withRefreshedCatalogCleaned = conn.withRefreshedCatalog
        ? { withRefreshedCatalog: conn.withRefreshedCatalog }
        : null;

      return service.update({ ...conn, ...withRefreshedCatalogCleaned });
    },
    {
      onSuccess: (data) => {
        queryClient.setQueryData(connectionsKeys.detail(data.connectionId), data);
      },
    }
  );
};

const useConnectionList = (): ListConnection => {
  const workspace = useCurrentWorkspace();
  const service = useWebConnectionService();

  return useSuspenseQuery(connectionsKeys.lists(), () => service.list(workspace.workspaceId));
};

const invalidateConnectionsList = async (queryClient: QueryClient) => {
  await queryClient.invalidateQueries(connectionsKeys.lists());
};

export {
  useConnectionList,
  useGetConnection,
  useUpdateConnection,
  useCreateConnection,
  useDeleteConnection,
  invalidateConnectionsList,
};
