import { useCallback } from "react";
import { useIntl } from "react-intl";
import { QueryClient, useMutation, useQueryClient } from "react-query";

import { getFrequencyType } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { useUser } from "core/AuthContext";
import { SyncSchema } from "core/domain/catalog";
import { WebBackendConnectionService } from "core/domain/connection";
import { ConnectionService } from "core/domain/connection/ConnectionService";
import {
  FilterConnectionRequestBody,
  ReadConnectionFilters,
  WebBackendFilteredConnectionReadList,
} from "core/request/DaspireClient";
import { useInitService } from "services/useInitService";

// import { useConfig } from "../../config";
import {
  ConnectionScheduleData,
  ConnectionScheduleType,
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
import { useAnalyticsService } from "./Analytics";
import { useCurrentWorkspace } from "./useWorkspace";

export const connectionsKeys = {
  all: [SCOPE_WORKSPACE, "connections"] as const,
  lists: () => [...connectionsKeys.all, "list"] as const,
  list: (filters: string) => [...connectionsKeys.lists(), { filters }] as const,
  filtersLists: () => [...connectionsKeys.lists(), "filtersLists"] as const,
  filteredList: (filters: FilterConnectionRequestBody) => [...connectionsKeys.lists(), { filters }] as const,
  detail: (connectionId: string) => [...connectionsKeys.all, "details", connectionId] as const,
  getState: (connectionId: string) => [...connectionsKeys.all, "getState", connectionId] as const,
};

export interface ValuesProps {
  name?: string;
  scheduleData: ConnectionScheduleData;
  scheduleType: ConnectionScheduleType;
  prefix: string;
  syncCatalog: SyncSchema;
  namespaceDefinition: NamespaceDefinitionType;
  namespaceFormat?: string;
  operations?: OperationCreate[];
}

interface CreateConnectionProps {
  values: ValuesProps;
  source: SourceRead;
  destination: DestinationRead;
  sourceDefinition?: Pick<SourceDefinitionRead, "sourceDefinitionId">;
  destinationDefinition?: { name: string; destinationDefinitionId: string };
  sourceCatalogId: string | undefined;
}

export interface ListConnection {
  connections: WebBackendConnectionRead[];
}

function useWebConnectionService() {
  // const config = useConfig();
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(
    () => new WebBackendConnectionService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares]
  );
}

export function useConnectionService() {
  // const config = useConfig();
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(
    () => new ConnectionService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares]
  );
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
    analyticsService.track(Namespace.CONNECTION, Action.SYNC, {
      actionDescription: "Manual triggered sync",
      connector_source: connection.source?.sourceName,
      connector_source_definition_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: getFrequencyType(connection.scheduleData?.basicSchedule),
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

      analyticsService.track(Namespace.CONNECTION, Action.CREATE, {
        actionDescription: "New connection created",
        frequency: getFrequencyType(values.scheduleData?.basicSchedule),
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
  const analyticsService = useAnalyticsService();

  return useMutation((connection: WebBackendConnectionRead) => service.delete(connection.connectionId), {
    onSuccess: (_data, connection) => {
      analyticsService.track(Namespace.CONNECTION, Action.DELETE, {
        actionDescription: "Connection deleted",
        connector_source: connection.source?.sourceName,
        connector_source_definition_id: connection.source?.sourceDefinitionId,
        connector_destination: connection.destination?.destinationName,
        connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      });

      queryClient.removeQueries(connectionsKeys.detail(connection.connectionId));
      queryClient.setQueryData(
        connectionsKeys.lists(),
        (lst: ListConnection | undefined) =>
          ({
            connections: lst?.connections.filter((conn) => conn.connectionId !== connection.connectionId) ?? [],
          } as ListConnection)
      );
    },
  });
};

const useUpdateConnection = () => {
  const service = useWebConnectionService();
  const queryClient = useQueryClient();

  return useMutation((connectionUpdate: WebBackendConnectionUpdate) => service.update(connectionUpdate), {
    onSuccess: (connection) => {
      queryClient.setQueryData(connectionsKeys.detail(connection.connectionId), connection);
    },
  });
};

export const useRemoveConnectionsFromList = (): ((connectionIds: string[]) => void) => {
  const queryClient = useQueryClient();

  return useCallback(
    (connectionIds: string[]) => {
      queryClient.setQueryData(connectionsKeys.lists(), (ls: ListConnection | undefined) => ({
        ...ls,
        connections: ls?.connections.filter((c) => !connectionIds.includes(c.connectionId)) ?? [],
      }));
    },
    [queryClient]
  );
};

const useConnectionList = (): ListConnection => {
  const workspace = useCurrentWorkspace();
  const service = useWebConnectionService();
  return useSuspenseQuery(connectionsKeys.lists(), () => service.list(workspace.workspaceId));
};

const useFilteredConnectionList = (filters: FilterConnectionRequestBody): WebBackendFilteredConnectionReadList => {
  const service = useWebConnectionService();

  return useSuspenseQuery(connectionsKeys.filteredList(filters), () => service.filteredList(filters));
};

const useConnectionFilters = (): ReadConnectionFilters => {
  const service = useWebConnectionService();

  return useSuspenseQuery(connectionsKeys.filtersLists(), () => service.filtersLists());
};

const useConnectionFilterOptions = () => {
  const { formatMessage } = useIntl();
  const { status, sources, destinations } = useConnectionFilters();

  const statusOptions = status
    .map((statusOption) => {
      return {
        label: statusOption.key,
        value: statusOption.value,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));

  const sourceOptions = sources
    .map((source) => {
      return {
        label: source.key,
        value: source.value,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));

  const destinationOptions = destinations
    .map((destination) => {
      return {
        label: destination.key,
        value: destination.value,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));

  return {
    statusOptions: [{ label: formatMessage({ id: "connection.filter.allStatus" }), value: "" }, ...statusOptions],
    sourceOptions: [{ label: formatMessage({ id: "connection.filter.allSources" }), value: "" }, ...sourceOptions],
    destinationOptions: [
      { label: formatMessage({ id: "connection.filter.allDestinations" }), value: "" },
      ...destinationOptions,
    ],
  };
};

const invalidateConnectionsList = async (queryClient: QueryClient) => {
  await queryClient.invalidateQueries(connectionsKeys.lists());
};

const useGetConnectionState = (connectionId: string) => {
  const service = useConnectionService();

  return useSuspenseQuery(connectionsKeys.getState(connectionId), () => service.getState(connectionId));
};

export {
  useConnectionList,
  useFilteredConnectionList,
  useConnectionFilters,
  useConnectionFilterOptions,
  useGetConnection,
  useUpdateConnection,
  useCreateConnection,
  useDeleteConnection,
  invalidateConnectionsList,
  useGetConnectionState,
};
