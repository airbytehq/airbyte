import { useFetcher } from "rest-hooks";

import config from "../../../config";
import SourceImplementationResource from "../../../core/resources/SourceImplementation";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";

type ValuesProps = {
  name: string;
  serviceType?: string;
  sourceId?: string;
  connectionConfiguration?: any;
  frequency?: string;
};

type ConnectorProps = { name: string; sourceId: string };

const useSource = () => {
  const createSourcesImplementation = useFetcher(
    SourceImplementationResource.createShape()
  );

  const updateSourceImplementation = useFetcher(
    SourceImplementationResource.updateShape()
  );

  const recreateSourceImplementation = useFetcher(
    SourceImplementationResource.recreateShape()
  );

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
      connector_source_id: sourceConnector?.sourceId
    });

    try {
      const result = await createSourcesImplementation(
        {},
        {
          name: values.name,
          workspaceId: config.ui.workspaceId,
          sourceId: values.sourceId,
          connectionConfiguration: values.connectionConfiguration
        },
        [
          [
            SourceImplementationResource.listShape(),
            { workspaceId: config.ui.workspaceId },
            (
              newSourceImplementationId: string,
              sourcesImplementationIds: { sources: string[] }
            ) => ({
              sources: [
                ...(sourcesImplementationIds?.sources || []),
                newSourceImplementationId
              ]
            })
          ]
        ]
      );
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - success",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceId
      });

      return result;
    } catch (e) {
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - failure",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceId
      });
      throw e;
    }
  };

  const updateSource = async ({
    values,
    sourceImplementationId
  }: {
    values: ValuesProps;
    sourceImplementationId: string;
  }) => {
    return await updateSourceImplementation(
      {
        sourceImplementationId: sourceImplementationId
      },
      {
        name: values.name,
        sourceImplementationId,
        connectionConfiguration: values.connectionConfiguration
      }
    );
  };

  const recreateSource = async ({
    values,
    sourceImplementationId
  }: {
    values: ValuesProps;
    sourceImplementationId: string;
  }) => {
    return await recreateSourceImplementation(
      {
        sourceImplementationId: sourceImplementationId
      },
      {
        name: values.name,
        sourceImplementationId,
        connectionConfiguration: values.connectionConfiguration,
        workspaceId: config.ui.workspaceId,
        sourceId: values.sourceId
      },
      // Method used only in onboarding.
      // Replace all SourceImplementation List to new item in UpdateParams (to change id)
      [
        [
          SourceImplementationResource.listShape(),
          { workspaceId: config.ui.workspaceId },
          (newSourceImplementationId: string) => ({
            sources: [newSourceImplementationId]
          })
        ]
      ]
    );
  };

  return { createSource, updateSource, recreateSource };
};

export default useSource;
