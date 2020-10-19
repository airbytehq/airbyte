import { useFetcher, useResource } from "rest-hooks";

import config from "../../../config";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import ConnectionResource, {
  Connection
} from "../../../core/resources/Connection";
import WorkspaceResource from "../../../core/resources/Workspace";
import { SyncSchema } from "../../../core/resources/Schema";
import { Source } from "../../../core/resources/Source";
import FrequencyConfig from "../../../data/FrequencyConfig.json";
import { SourceImplementation } from "../../../core/resources/SourceImplementation";

type ValuesProps = {
  frequency: string;
  syncSchema: SyncSchema;
  source?: { name: string; sourceId: string };
};

type CreateConnectionProps = {
  values: ValuesProps;
  sourceImplementation?: SourceImplementation;
  destinationImplementationId: string;
  sourceConnector?: Source;
  destinationConnector?: { name: string; destinationId: string };
};

const useConnection = () => {
  const createConnectionResource = useFetcher(ConnectionResource.createShape());
  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: config.ui.workspaceId
  });
  const updateConnectionResource = useFetcher(ConnectionResource.updateShape());
  const updateStateConnectionResource = useFetcher(
    ConnectionResource.updateStateShape()
  );
  const createConnection = async ({
    values,
    sourceImplementation,
    destinationImplementationId,
    sourceConnector,
    destinationConnector
  }: CreateConnectionProps) => {
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );

    try {
      const result = await createConnectionResource(
        {
          sourceId: values.source?.sourceId || "",
          sourceName: values.source?.name || "",
          name: sourceImplementation?.name || ""
        },
        {
          sourceImplementationId: sourceImplementation?.sourceImplementationId,
          destinationImplementationId,
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
        user_id: config.ui.workspaceId,
        action: "Set up connection",
        frequency: frequencyData?.text,
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceId,
        connector_destination: destinationConnector?.name,
        connector_destination_id: destinationConnector?.destinationId
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
    await updateConnectionResource(
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
    sourceData,
    sourceName,
    connectionConfiguration,
    schedule
  }: {
    sourceData: Connection;
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
        ...sourceData,
        schedule,
        source: {
          ...sourceData.source,
          name: sourceName,
          connectionConfiguration: connectionConfiguration
        }
      }
    );
  };

  return {
    createConnection,
    updateConnection,
    updateStateConnection
  };
};

export default useConnection;
