import { useFetcher, useResource } from "rest-hooks";

import config from "../../../config";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import ConnectionResource, {
  Connection
} from "../../../core/resources/Connection";
import WorkspaceResource from "../../../core/resources/Workspace";
import { SyncSchema } from "../../../core/resources/Schema";
import { SourceDefinition } from "../../../core/resources/SourceDefinition";
import FrequencyConfig from "../../../data/FrequencyConfig.json";
import { Source } from "../../../core/resources/Source";
import { Routes } from "../../../pages/routes";
import useRouter from "../useRouterHook";
import { Destination } from "../../../core/resources/Destination";

type ValuesProps = {
  frequency: string;
  syncSchema: SyncSchema;
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

const useConnection = () => {
  const { push, history } = useRouter();

  const createConnectionResource = useFetcher(ConnectionResource.createShape());
  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: config.ui.workspaceId
  });
  const updateConnectionResource = useFetcher(ConnectionResource.updateShape());
  const updateStateConnectionResource = useFetcher(
    ConnectionResource.updateStateShape()
  );
  const deleteConnectionResource = useFetcher(ConnectionResource.deleteShape());

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
          syncMode: "full_refresh",
          schedule: frequencyData?.config,
          status: "active",
          syncSchema: values.syncSchema
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
        airbyte_version: config.version,
        user_id: config.ui.workspaceId,
        action: "Set up connection",
        frequency: frequencyData?.text,
        connector_source_definition: sourceDefinition?.name,
        connector_source_definition_id: sourceDefinition?.sourceDefinitionId,
        connector_destination: destinationDefinition?.name,
        connector_destination_definition_id:
          destinationDefinition?.destinationDefinitionId
      });

      if (!workspace.onboardingComplete) {
        await updateWorkspace(
          {},
          {
            workspaceId: workspace.workspaceId,
            initialSetupComplete: workspace.initialSetupComplete,
            onboardingComplete: true,
            anonymousDataCollection: workspace.anonymousDataCollection,
            news: workspace.news,
            securityUpdates: workspace.securityUpdates
          }
        );
      }

      return result;
    } catch (e) {
      throw e;
    }
  };

  const updateConnection = async ({
    connectionId,
    syncSchema,
    status,
    schedule
  }: {
    connectionId: string;
    syncSchema?: SyncSchema;
    status: string;
    schedule: {
      units: number;
      timeUnit: string;
    } | null;
  }) => {
    return await updateConnectionResource(
      {},
      {
        connectionId,
        syncSchema,
        status,
        schedule
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

  return {
    createConnection,
    updateConnection,
    updateStateConnection,
    deleteConnection
  };
};

export default useConnection;
