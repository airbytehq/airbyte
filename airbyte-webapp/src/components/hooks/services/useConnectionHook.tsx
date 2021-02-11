import { useCallback, useEffect, useState } from "react";
import { useFetcher, useResource } from "rest-hooks";

import config from "../../../config";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import ConnectionResource, {
  Connection
} from "../../../core/resources/Connection";
import { SyncSchema } from "../../../core/domain/catalog";
import { SourceDefinition } from "../../../core/resources/SourceDefinition";
import FrequencyConfig from "../../../data/FrequencyConfig.json";
import { Source } from "../../../core/resources/Source";
import { Routes } from "../../../pages/routes";
import useRouter from "../useRouterHook";
import { Destination } from "../../../core/resources/Destination";
import useWorkspace from "./useWorkspaceHook";

type ValuesProps = {
  frequency: string;
  syncCatalog: SyncSchema;
  source?: { name: string; sourceId: string };
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

export const useConnectionLoad = (
  connectionId: string,
  withRefresh?: boolean
) => {
  const [connection, setConnection] = useState<null | Connection>(null);
  const [isLoadingConnection, setIsLoadingConnection] = useState(false);

  // TODO: change to useStatefulResource
  const fetchConnection = useFetcher(ConnectionResource.detailShape(), false);
  const baseConnection = useResource(ConnectionResource.detailShape(), {
    connectionId
  });

  useEffect(() => {
    (async () => {
      if (withRefresh) {
        setIsLoadingConnection(true);
        setConnection(
          await fetchConnection({
            connectionId,
            withRefreshedCatalog: withRefresh
          })
        );

        setIsLoadingConnection(false);
      }
    })();
  }, [connectionId, fetchConnection, withRefresh]);

  return {
    connection: withRefresh ? connection : baseConnection,
    isLoadingConnection
  };
};

const useConnection = () => {
  const { push, history } = useRouter();
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
    destinationDefinition
  }: CreateConnectionProps) => {
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );

    try {
      const result = await createConnectionResource(
        {
          source: {
            sourceId: source?.sourceId || "",
            sourceName: source?.sourceName || "",
            name: source?.name || ""
          },
          destination: {
            destinationId: destination?.destinationId || "",
            destinationName: destination?.destinationName || "",
            name: destination?.name || ""
          }
        },
        {
          sourceId: source?.sourceId,
          destinationId: destination?.destinationId,
          schedule: frequencyData?.config,
          status: "active",
          syncCatalog: values.syncCatalog
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
                newConnectionId
              ]
            })
          ]
        ]
      );
      AnalyticsService.track("New Connection - Action", {
        user_id: config.ui.workspaceId,
        action: "Set up connection",
        frequency: frequencyData?.text,
        connector_source_definition: source?.sourceName,
        connector_source_definition_id: sourceDefinition?.sourceDefinitionId,
        connector_destination_definition: destination?.destinationName,
        connector_destination_definition_id:
          destinationDefinition?.destinationDefinitionId
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
    connectionId,
    syncCatalog,
    status,
    schedule,
    withRefreshedCatalog
  }: {
    connectionId: string;
    syncCatalog?: SyncSchema;
    status: string;
    schedule: {
      units: number;
      timeUnit: string;
    } | null;
    withRefreshedCatalog?: boolean;
  }) => {
    const withRefreshedCatalogCleaned = withRefreshedCatalog
      ? { withRefreshedCatalog }
      : null;

    return await updateConnectionResource(
      {},
      {
        connectionId,
        syncCatalog,
        status,
        schedule,
        ...withRefreshedCatalogCleaned
      }
    );
  };

  const updateStateConnection = async ({
    connection,
    sourceName,
    connectionConfiguration,
    schedule
  }: {
    connection: Connection;
    sourceName: string;
    connectionConfiguration: any;
    schedule: {
      units: number;
      timeUnit: string;
    } | null;
  }) => {
    await updateStateConnectionResource(
      {},
      {
        ...connection,
        schedule,
        source: {
          ...connection.source,
          name: sourceName,
          connectionConfiguration: connectionConfiguration
        }
      }
    );
  };

  const deleteConnection = async ({
    connectionId
  }: {
    connectionId: string;
  }) => {
    await deleteConnectionResource({ connectionId });

    history.length > 2 ? history.goBack() : push(Routes.Source);
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
    deleteConnection
  };
};

export default useConnection;
