import { useFetcher } from "rest-hooks";

import config from "../../../config";
import SourceResource from "../../../core/resources/Source";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: any;
  frequency?: string;
};

type ConnectorProps = { name: string; sourceDefinitionId: string };

const useSource = () => {
  const createSourcesImplementation = useFetcher(SourceResource.createShape());

  const updatesource = useFetcher(SourceResource.updateShape());

  const recreatesource = useFetcher(SourceResource.recreateShape());

  const createSource = async ({
    values,
    sourceConnector
  }: {
    values: ValuesProps;
    sourceConnector?: ConnectorProps;
  }) => {
    AnalyticsService.track("New Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Test a connector",
      connector_source: sourceConnector?.name,
      connector_source_id: sourceConnector?.sourceDefinitionId
    });

    try {
      const result = await createSourcesImplementation(
        {},
        {
          name: values.name,
          sourceDefinitionId: sourceConnector?.sourceDefinitionId,
          workspaceId: config.ui.workspaceId,
          connectionConfiguration: values.connectionConfiguration
        },
        [
          [
            SourceResource.listShape(),
            { workspaceId: config.ui.workspaceId },
            (newsourceId: string, sourceIds: { sources: string[] }) => ({
              sources: [...(sourceIds?.sources || []), newsourceId]
            })
          ]
        ]
      );
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - success",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceDefinitionId
      });

      return result;
    } catch (e) {
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - failure",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceDefinitionId
      });
      throw e;
    }
  };

  const updateSource = async ({
    values,
    sourceId
  }: {
    values: ValuesProps;
    sourceId: string;
  }) => {
    return await updatesource(
      {
        sourceId: sourceId
      },
      {
        name: values.name,
        sourceId,
        connectionConfiguration: values.connectionConfiguration
      }
    );
  };

  const recreateSource = async ({
    values,
    sourceId
  }: {
    values: ValuesProps;
    sourceId: string;
  }) => {
    return await recreatesource(
      {
        sourceId: sourceId
      },
      {
        name: values.name,
        sourceId,
        connectionConfiguration: values.connectionConfiguration,
        workspaceId: config.ui.workspaceId,
        sourceDefinitionId: values.serviceType
      },
      // Method used only in onboarding.
      // Replace all source List to new item in UpdateParams (to change id)
      [
        [
          SourceResource.listShape(),
          { workspaceId: config.ui.workspaceId },
          (newsourceId: string) => ({
            sources: [newsourceId]
          })
        ]
      ]
    );
  };

  return { createSource, updateSource, recreateSource };
};

export default useSource;
