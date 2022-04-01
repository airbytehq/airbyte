import { useFetcher, useResource } from "rest-hooks";

import SourceResource from "core/resources/Source";
import ConnectionResource, { Connection } from "core/resources/Connection";
import { ConnectionConfiguration } from "core/domain/connection";
import useWorkspace from "./useWorkspace";

import useRouter from "hooks/useRouter";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { Source } from "core/domain/connector";
import { RoutePaths } from "../../pages/routePaths";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
  frequency?: string;
};

type ConnectorProps = { name: string; sourceDefinitionId: string };

type SourceService = {
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
  const { workspace } = useWorkspace();
  const createSourcesImplementation = useFetcher(SourceResource.createShape());
  const analyticsService = useAnalyticsService();

  const updatesource = useFetcher(SourceResource.partialUpdateShape());

  const sourceDelete = useFetcher(SourceResource.deleteShape());

  const updateConnectionsStore = useFetcher(
    ConnectionResource.updateStoreAfterDeleteShape()
  );

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
      // analyticsService.track("New Source - Action", {
      //   action: "Test a connector",
      //   connector_source: sourceConnector?.name,
      //   connector_source_definition_id: sourceConnector?.sourceDefinitionId,
      // });

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
  }) =>
    await updatesource(
      {
        sourceId: sourceId,
      },
      {
        name: values.name,
        sourceId,
        connectionConfiguration: values.connectionConfiguration,
      }
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
    connectionsWithSource.map((item) =>
      updateConnectionsStore({ connectionId: item.connectionId }, undefined)
    );

    push(RoutePaths.Source);
  };

  return {
    createSource,
    updateSource,
    deleteSource,
  };
};

const useSourceList = (): { sources: Source[] } => {
  const { workspace } = useWorkspace();
  return useResource(SourceResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useSourceList };
export default useSource;
