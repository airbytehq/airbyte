import { useCallback } from "react";
import { useFetcher, useResource } from "rest-hooks";
import { useStatefulResource } from "@rest-hooks/legacy";

import SourceResource, { Source } from "core/resources/Source";
import { Routes } from "pages/routes";
import ConnectionResource, { Connection } from "core/resources/Connection";
import SourceDefinitionSpecificationResource, {
  SourceDefinitionSpecification,
} from "core/resources/SourceDefinitionSpecification";
import SchedulerResource, { Scheduler } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";
import useWorkspace from "./useWorkspace";

import useRouter from "hooks/useRouter";
import { useAnalytics } from "hooks/useAnalytics";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
  frequency?: string;
};

type ConnectorProps = { name: string; sourceDefinitionId: string };

export const useSourceDefinitionSpecificationLoad = (
  sourceDefinitionId: string
): {
  isLoading: boolean;
  error?: Error;
  sourceDefinitionSpecification?: SourceDefinitionSpecification;
} => {
  const {
    loading: isLoading,
    error,
    data: sourceDefinitionSpecification,
  } = useStatefulResource(
    SourceDefinitionSpecificationResource.detailShape(),
    sourceDefinitionId
      ? {
          sourceDefinitionId,
        }
      : null
  );

  return { sourceDefinitionSpecification, error, isLoading };
};

type SourceService = {
  recreateSource: (recreateSourcePayload: {
    values: ValuesProps;
    sourceId: string;
  }) => Promise<Source>;
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
  const { workspace } = useWorkspace();
  const createSourcesImplementation = useFetcher(SourceResource.createShape());
  const analyticsService = useAnalytics();

  const sourceCheckConnectionShape = useFetcher(
    SchedulerResource.sourceCheckConnectionShape()
  );

  const updatesource = useFetcher(SourceResource.partialUpdateShape());

  const recreatesource = useFetcher(SourceResource.recreateShape());

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

  const recreateSource: SourceService["recreateSource"] = async ({
    values,
    sourceId,
  }) => {
    return await recreatesource(
      {
        sourceId: sourceId,
      },
      {
        name: values.name,
        sourceId,
        connectionConfiguration: values.connectionConfiguration,
        workspaceId: workspace.workspaceId,
        sourceDefinitionId: values.serviceType,
      },
      // Method used only in onboarding.
      // Replace all source List to new item in UpdateParams (to change id)
      [
        [
          SourceResource.listShape(),
          { workspaceId: workspace.workspaceId },
          (newsourceId: string) => ({
            sources: [newsourceId],
          }),
        ],
      ]
    );
  };

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

    push(Routes.Root);
  };

  return {
    createSource,
    updateSource,
    recreateSource,
    deleteSource,
    checkSourceConnection,
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
