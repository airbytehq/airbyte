import { useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import FrequencyConfig from "config/FrequencyConfig.json";
import { SyncSchema } from "core/domain/catalog";
import {
  Connection,
  ConnectionNamespaceDefinition,
  ConnectionStatus,
  ScheduleProperties,
  WebBackendConnectionService,
} from "core/domain/connection";
import { ConnectionService } from "core/domain/connection/ConnectionService";
import { Operation } from "core/domain/connection/operation";
import { Destination, Source, SourceDefinition } from "core/domain/connector";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { equal } from "utils/objects";

import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";
import { SCOPE_WORKSPACE } from "../../services/Scope";
import { useCurrentWorkspace } from "./useWorkspace";

export const connectionsKeys = {
  all: [SCOPE_WORKSPACE, "connections"] as const,
  lists: () => [...connectionsKeys.all, "list"] as const,
  list: (filters: string) => [...connectionsKeys.lists(), { filters }] as const,
  detail: (connectionId: string) => [...connectionsKeys.all, "details", connectionId] as const,
};

export type ValuesProps = {
  schedule: ScheduleProperties | null;
  prefix: string;
  syncCatalog: SyncSchema;
  namespaceDefinition: ConnectionNamespaceDefinition;
  namespaceFormat?: string;
  operations?: Operation[];
};

type CreateConnectionProps = {
  values: ValuesProps;
  source?: Source;
  destination?: Destination;
  sourceDefinition?: SourceDefinition | { name: string; sourceDefinitionId: string };
  destinationDefinition?: { name: string; destinationDefinitionId: string };
  sourceCatalogId: string;
};

type UpdateConnection = {
  connectionId: string;
  syncCatalog?: SyncSchema;
  namespaceDefinition: ConnectionNamespaceDefinition;
  namespaceFormat?: string;
  status: ConnectionStatus;
  prefix: string;
  schedule?: ScheduleProperties | null;
  operations?: Operation[];
  withRefreshedCatalog?: boolean;
  sourceCatalogId?: string;
};

export type ListConnection = { connections: Connection[] };

function useWebConnectionService(): WebBackendConnectionService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new WebBackendConnectionService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config, middlewares]
  );
}

function useConnectionService(): ConnectionService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new ConnectionService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config, middlewares]
  );
}

export const useConnectionLoad = (
  connectionId: string
): {
  connection: Connection;
  refreshConnectionCatalog: () => Promise<Connection>;
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

  return useMutation((connection: Connection) => {
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

const useGetConnection = (connectionId: string, options?: { refetchInterval: number }): Connection => {
  const service = useWebConnectionService();

  return useSuspenseQuery(connectionsKeys.detail(connectionId), () => service.getConnection(connectionId), options);
};

const useCreateConnection = () => {
  const service = useWebConnectionService();
  const queryClient = useQueryClient();
  const analyticsService = useAnalyticsService();

  return useMutation(
    async (conn: CreateConnectionProps) => {
      const { values, source, destination, sourceDefinition, destinationDefinition, sourceCatalogId } = conn;
      const response = await service.create({
        sourceId: source?.sourceId,
        destinationId: destination?.destinationId,
        ...values,
        status: "active",
        sourceCatalogId: sourceCatalogId,
      });

      const enabledStreams = values.syncCatalog.streams.filter((stream) => stream.config.selected).length;

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
    (conn: UpdateConnection) => {
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

export { useConnectionList, useGetConnection, useUpdateConnection, useCreateConnection, useDeleteConnection };
