import { useFetcher } from "rest-hooks";

import config from "../../../config";
import DestinationResource from "../../../core/resources/Destination";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: any;
};

type ConnectorProps = { name: string; destinationDefinitionId: string };

const useDestination = () => {
  const createDestinationsImplementation = useFetcher(
    DestinationResource.createShape()
  );

  const updatedestination = useFetcher(DestinationResource.updateShape());

  const recreatedestination = useFetcher(DestinationResource.recreateShape());

  const createDestination = async ({
    values,
    destinationConnector
  }: {
    values: ValuesProps;
    destinationConnector?: ConnectorProps;
  }) => {
    AnalyticsService.track("New Destination - Action", {
      user_id: config.ui.workspaceId,
      action: "Test a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id:
        destinationConnector?.destinationDefinitionId
    });

    try {
      const result = await createDestinationsImplementation(
        {},
        {
          name: values.name,
          destinationDefinitionId:
            destinationConnector?.destinationDefinitionId,
          workspaceId: config.ui.workspaceId,
          connectionConfiguration: values.connectionConfiguration
        },
        [
          [
            DestinationResource.listShape(),
            { workspaceId: config.ui.workspaceId },
            (
              newdestinationId: string,
              destinationIds: { destinations: string[] }
            ) => ({
              destinationDefinitions: [
                ...(destinationIds?.destinations || []),
                newdestinationId
              ]
            })
          ]
        ]
      );

      AnalyticsService.track("New Destination - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - success",
        connector_destination: destinationConnector?.name,
        connector_destination_definition_id:
          destinationConnector?.destinationDefinitionId
      });

      return result;
    } catch (e) {
      AnalyticsService.track("New Destination - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - failure",
        connector_destination: destinationConnector?.name,
        connector_destination_definition_id:
          destinationConnector?.destinationDefinitionId
      });
      throw e;
    }
  };

  const updateDestination = async ({
    values,
    destinationId
  }: {
    values: ValuesProps;
    destinationId: string;
  }) => {
    return await updatedestination(
      {
        destinationId
      },
      {
        name: values.name,
        destinationId,
        connectionConfiguration: values.connectionConfiguration
      }
    );
  };

  const recreateDestination = async ({
    values,
    destinationId
  }: {
    values: ValuesProps;
    destinationId: string;
  }) => {
    return await recreatedestination(
      {
        destinationId
      },
      {
        name: values.name,
        destinationId,
        connectionConfiguration: values.connectionConfiguration,
        workspaceId: config.ui.workspaceId,
        destinationDefinitionId: values.serviceType
      },
      // Method used only in onboarding.
      // Replace all destination List to new item in UpdateParams (to change id)
      [
        [
          DestinationResource.listShape(),
          { workspaceId: config.ui.workspaceId },
          (newdestinationId: string) => ({
            destinations: [newdestinationId]
          })
        ]
      ]
    );
  };

  return { createDestination, updateDestination, recreateDestination };
};

export default useDestination;
