import { useCallback, useEffect, useState } from "react";
import { useFetcher, useResource } from "rest-hooks";

import config from "config";
import { AnalyticsService } from "core/analytics/AnalyticsService";
import ConnectionResource, {
  Connection,
  ScheduleProperties,
} from "core/resources/Connection";
import { SyncSchema } from "core/domain/catalog";
import { SourceDefinition } from "core/resources/SourceDefinition";
import FrequencyConfig from "config/FrequencyConfig.json";
import { Source } from "core/resources/Source";
import { Routes } from "pages/routes";
import useRouter from "../useRouterHook";
import { Destination } from "core/resources/Destination";
import useWorkspace from "./useWorkspaceHook";
import {
  ConnectionConfiguration,
  ConnectionNamespaceDefinition,
} from "core/domain/connection";
import { Operation } from "core/domain/connection/operation";
import { equal } from "utils/objects";

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

type UpdateStateConnection = {
  connection: Connection;
  sourceName: string;
  prefix: string;
  connectionConfiguration: ConnectionConfiguration;
  schedule: {
    units: number;
    timeUnit: string;
  } | null;
};

export const useConnectionLoad = (
  connectionId: string,
  withRefresh?: boolean
): { connection: Connection | null; isLoadingConnection: boolean } => {
  const [connection, setConnection] = useState<null | Connection>(null);
  const [isLoadingConnection, setIsLoadingConnection] = useState(false);

  // TODO: change to useStatefulResource
  const fetchConnection = useFetcher(ConnectionResource.detailShape(), false);
  const baseConnection = useResource(ConnectionResource.detailShape(), {
    connectionId,
  });

  useEffect(() => {
    (async () => {
      if (withRefresh) {
        setIsLoadingConnection(true);
        setConnection(
          await fetchConnection({
            connectionId,
            withRefreshedCatalog: withRefresh,
          })
        );

        setIsLoadingConnection(false);
      }
    })();
  }, [connectionId, fetchConnection, withRefresh]);

  return {
    connection: withRefresh ? connection : baseConnection,
    isLoadingConnection,
  };
};

const useConnection = (): {
  createConnection: (conn: CreateConnectionProps) => Promise<Connection>;
  updateConnection: (conn: UpdateConnection) => Promise<Connection>;
  updateStateConnection: (conn: UpdateStateConnection) => Promise<void>;
  resetConnection: (connId: string) => Promise<void>;
  deleteConnection: (payload: { connectionId: string }) => Promise<void>;
} => {
  const { push } = useRouter();
  const { finishOnboarding, workspace } = useWorkspace();

  const createConnectionResource = useFetcher(ConnectionResource.createShape());
  const updateConnectionResource = useFetcher(ConnectionResource.updateShape());
  const updateStateConnectionResource = useFetcher(
    ConnectionResource.updateStateShape()
  );
  const deleteConnectionResource = useFetcher(ConnectionResource.deleteShape());
  const resetConnectionResource = useFetcher(ConnectionResource.reset());

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
            { workspaceId: config.ui.workspaceId },
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

      AnalyticsService.track("New Connection - Action", {
        user_id: config.ui.workspaceId,
        action: "Set up connection",
        frequency: frequencyData?.text,
        connector_source_definition: source?.sourceName,
        connector_source_definition_id: sourceDefinition?.sourceDefinitionId,
        connector_destination_definition: destination?.destinationName,
        connector_destination_definition_id:
          destinationDefinition?.destinationDefinitionId,
      });
      if (workspace.displaySetupWizard) {
        await finishOnboarding();
      }

      return result;
    } catch (e) {
      throw e;
    }
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

  const updateStateConnection = async ({
    connection,
    sourceName,
    connectionConfiguration,
    schedule,
    prefix,
  }: UpdateStateConnection) => {
    await updateStateConnectionResource(
      {},
      {
        ...connection,
        schedule,
        prefix,
        source: {
          ...connection.source,
          name: sourceName,
          connectionConfiguration: connectionConfiguration,
        },
      }
    );
  };

  const deleteConnection = async ({
    connectionId,
  }: {
    connectionId: string;
  }) => {
    await deleteConnectionResource({ connectionId });

    push(Routes.Connections);
  };

  const resetConnection = useCallback(
    async (connectionId: string) => {
      await resetConnectionResource({ connectionId });
    },
    [resetConnectionResource]
  );

  return {
    createConnection,
    updateConnection,
    updateStateConnection,
    resetConnection,
    deleteConnection,
  };
};
export default useConnection;
