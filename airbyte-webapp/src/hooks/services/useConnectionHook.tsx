import { useFetcher, useResource } from "rest-hooks";
import { useMutation } from "react-query";

import FrequencyConfig from "config/FrequencyConfig.json";
import { useConfig } from "config";
import {
  Connection,
  ConnectionNamespaceDefinition,
  WebBackendConnectionService,
} from "core/domain/connection";

import ConnectionResource, {
  ScheduleProperties,
} from "core/resources/Connection";
import { SyncSchema } from "core/domain/catalog";
import useWorkspace from "./useWorkspace";
import { Operation } from "core/domain/connection/operation";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import useRouter from "hooks/useRouter";

import { equal } from "utils/objects";
import { Destination, Source, SourceDefinition } from "core/domain/connector";
import { RoutePaths } from "pages/routePaths";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { ConnectionService } from "core/domain/connection/ConnectionService";

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
  sourceDefinition?:
    | SourceDefinition
    | { name: string; sourceDefinitionId: string };
  destinationDefinition?: { name: string; destinationDefinitionId: string };
};

type UpdateConnection = {
  connectionId: string;
  syncCatalog?: SyncSchema;
  namespaceDefinition: ConnectionNamespaceDefinition;
  namespaceFormat?: string;
  status: string;
  prefix: string;
  schedule?: ScheduleProperties | null;
  operations?: Operation[];
  withRefreshedCatalog?: boolean;
};

function useWebConnectionService(): WebBackendConnectionService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new WebBackendConnectionService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

function useConnectionService(): ConnectionService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new ConnectionService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

export const useConnectionLoad = (
  connectionId: string
): {
  connection: Connection;
  refreshConnectionCatalog: () => Promise<Connection>;
} => {
  const connection = useResource(ConnectionResource.detailShape(), {
    connectionId,
  });

  const connectionService = useWebConnectionService();

  const refreshConnectionCatalog = async () =>
    await connectionService.getConnection(connectionId, true);

  return {
    connection,
    refreshConnectionCatalog,
  };
};

export const useSyncConnection = () => {
  const service = useConnectionService();
  const analyticsService = useAnalyticsService();

  return useMutation((connection: Connection) => {
    const frequency = FrequencyConfig.find((item) =>
      equal(item.config, connection.schedule)
    );

    analyticsService.track("Source - Action", {
      action: "Full refresh sync",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequency?.text,
    });

    return service.sync(connection.connectionId);
  });
};

export const useResetConnection = () => {
  const service = useConnectionService();

  return useMutation((connectionId: string) => service.reset(connectionId));
};

const useConnection = (): {
  createConnection: (conn: CreateConnectionProps) => Promise<Connection>;
  updateConnection: (conn: UpdateConnection) => Promise<Connection>;
  deleteConnection: (payload: { connectionId: string }) => Promise<void>;
} => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const analyticsService = useAnalyticsService();

  const createConnectionResource = useFetcher(ConnectionResource.createShape());
  const updateConnectionResource = useFetcher(ConnectionResource.updateShape());
  const deleteConnectionResource = useFetcher(
    ConnectionResource.deleteShapeItem()
  );

  const createConnection = async ({
    values,
    source,
    destination,
    sourceDefinition,
    destinationDefinition,
  }: CreateConnectionProps) => {
    try {
      const result = await createConnectionResource(
        {},
        {
          sourceId: source?.sourceId,
          destinationId: destination?.destinationId,
          ...values,
          status: "active",
        },
        [
          [
            ConnectionResource.listShape(),
            { workspaceId: workspace.workspaceId },
            (
              newConnectionId: string,
              connectionsIds: { connections: string[] }
            ) => ({
              connections: [
                ...(connectionsIds?.connections || []),
                newConnectionId,
              ],
            }),
          ],
        ]
      );

      const frequencyData = FrequencyConfig.find((item) =>
        equal(item.config, values.schedule)
      );

      analyticsService.track("New Connection - Action", {
        action: "Set up connection",
        frequency: frequencyData?.text,
        connector_source_definition: source?.sourceName,
        connector_source_definition_id: sourceDefinition?.sourceDefinitionId,
        connector_destination_definition: destination?.destinationName,
        connector_destination_definition_id:
          destinationDefinition?.destinationDefinitionId,
      });

      return result;
    } catch (e) {
      throw e;
    }
  };

  const updateConnectionsStore = useFetcher(ConnectionResource.listShape());

  const deleteConnection = async ({
    connectionId,
  }: {
    connectionId: string;
  }) => {
    await deleteConnectionResource({}, { connectionId }, [
      [
        ConnectionResource.listShape(),
        { workspaceId: workspace.workspaceId },
        (cId: string, connectionsIds: { connections: string[] }) => {
          const res = connectionsIds?.connections || [];
          const index = res.findIndex((c) => c === cId);

          return {
            connections: [...res.slice(0, index), ...res.slice(index + 1)],
          };
        },
      ],
    ]);

    await updateConnectionsStore({ workspaceId: workspace.workspaceId });

    push(RoutePaths.Connections);
  };

  const updateConnection = async ({
    withRefreshedCatalog,
    ...formValues
  }: UpdateConnection) => {
    const withRefreshedCatalogCleaned = withRefreshedCatalog
      ? { withRefreshedCatalog }
      : null;

    return await updateConnectionResource(
      {},
      {
        ...formValues,
        ...withRefreshedCatalogCleaned,
      }
    );
  };

  return {
    createConnection,
    updateConnection,
    deleteConnection,
  };
};

const useConnectionList = (): { connections: Connection[] } => {
  const { workspace } = useWorkspace();
  return useResource(ConnectionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useConnectionList };
export default useConnection;
