import { useCallback } from "react";
import { useFetcher, useResource } from "rest-hooks";
import { useQueryClient } from "react-query";

import SourceResource from "core/resources/Source";
import { Connection } from "core/domain/connection";
import SchedulerResource, { Scheduler } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";

import useRouter from "hooks/useRouter";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { Source } from "core/domain/connector";
import { RoutePaths } from "pages/routePaths";
import { connectionsKeys, ListConnection } from "./useConnectionHook";
import { useCurrentWorkspace } from "./useWorkspace";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
  frequency?: string;
};

type ConnectorProps = { name: string; sourceDefinitionId: string };

type SourceService = {
  checkSourceConnection: (checkSourceConnectionPayload: {
    sourceId: string;
    values?: ValuesProps;
  }) => Promise<Scheduler>;
  createSource: (createSourcePayload: {
    values: ValuesProps;
    sourceConnector?: ConnectorProps;
  }) => Promise<Source>;
  updateSource: (updateSourcePayload: {
    values: ValuesProps;
    sourceId: string;
  }) => Promise<Source>;
  deleteSource: (deleteSourcePayload: {
    source: Source;
    connectionsWithSource: Connection[];
  }) => Promise<void>;
};

const useSource = (): SourceService => {
  const { push } = useRouter();
  const workspace = useCurrentWorkspace();
  const createSourcesImplementation = useFetcher(SourceResource.createShape());
  const analyticsService = useAnalyticsService();

  const sourceCheckConnectionShape = useFetcher(
    SchedulerResource.sourceCheckConnectionShape()
  );

  const updatesource = useFetcher(SourceResource.partialUpdateShape());

  const sourceDelete = useFetcher(SourceResource.deleteShape());

  const queryClient = useQueryClient();

  const createSource: SourceService["createSource"] = async ({
    values,
    sourceConnector,
  }) => {
    analyticsService.track("New Source - Action", {
      action: "Test a connector",
      connector_source: sourceConnector?.name,
      connector_source_id: sourceConnector?.sourceDefinitionId,
    });

    try {
      await sourceCheckConnectionShape({
        sourceDefinitionId: sourceConnector?.sourceDefinitionId,
        connectionConfiguration: values.connectionConfiguration,
      });

      // Try to crete source
      const result = await createSourcesImplementation(
        {},
        {
          name: values.name,
          sourceDefinitionId: sourceConnector?.sourceDefinitionId,
          workspaceId: workspace.workspaceId,
          connectionConfiguration: values.connectionConfiguration,
        },
        [
          [
            SourceResource.listShape(),
            { workspaceId: workspace.workspaceId },
            (newsourceId: string, sourceIds: { sources: string[] }) => ({
              sources: [...(sourceIds?.sources || []), newsourceId],
            }),
          ],
        ]
      );
      analyticsService.track("New Source - Action", {
        action: "Tested connector - success",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceDefinitionId,
      });

      return result;
    } catch (e) {
      analyticsService.track("New Source - Action", {
        action: "Tested connector - failure",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceDefinitionId,
      });
      throw e;
    }
  };

  const updateSource: SourceService["updateSource"] = async ({
    values,
    sourceId,
  }) => {
    await sourceCheckConnectionShape({
      name: values.name,
      sourceId,
      connectionConfiguration: values.connectionConfiguration,
    });

    return await updatesource(
      {
        sourceId: sourceId,
      },
      {
        name: values.name,
        sourceId,
        connectionConfiguration: values.connectionConfiguration,
      }
    );
  };

  const checkSourceConnection = useCallback(
    async ({
      sourceId,
      values,
    }: {
      sourceId: string;
      values?: ValuesProps;
    }) => {
      if (values) {
        return await sourceCheckConnectionShape({
          connectionConfiguration: values.connectionConfiguration,
          name: values.name,
          sourceId: sourceId,
        });
      }
      return await sourceCheckConnectionShape({
        sourceId,
      });
    },
    [sourceCheckConnectionShape]
  );

  const deleteSource: SourceService["deleteSource"] = async ({
    source,
    connectionsWithSource,
  }) => {
    await sourceDelete({
      sourceId: source.sourceId,
    });

    analyticsService.track("Source - Action", {
      action: "Delete source",
      connector_source: source.sourceName,
      connector_source_id: source.sourceDefinitionId,
    });

    // To delete connections with current source from local store
    const connectionIds = connectionsWithSource.map(
      (item) => item.connectionId
    );

    queryClient.setQueryData(
      connectionsKeys.lists(),
      (ls: ListConnection | undefined) => ({
        connections:
          ls?.connections.filter((c) =>
            connectionIds.includes(c.connectionId)
          ) ?? [],
      })
    );

    push(RoutePaths.Source);
  };

  return {
    createSource,
    updateSource,
    deleteSource,
    checkSourceConnection,
  };
};

const useSourceList = (): { sources: Source[] } => {
  const workspace = useCurrentWorkspace();
  return useResource(SourceResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useSourceList };
export default useSource;
