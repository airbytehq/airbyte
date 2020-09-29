import { useFetcher } from "rest-hooks";

import config from "../../../config";
import SourceImplementationResource from "../../../core/resources/SourceImplementation";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";

type ValuesProps = {
  name: string;
  serviceType?: string;
  specificationId?: string;
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
          sourceSpecificationId: values.specificationId,
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

  return { createSource, updateSource };
};

export default useSource;
