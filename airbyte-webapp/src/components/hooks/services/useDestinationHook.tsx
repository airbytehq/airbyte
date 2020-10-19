import { useFetcher } from "rest-hooks";

import config from "../../../config";
import DestinationImplementationResource from "../../../core/resources/DestinationImplementation";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: any;
};

type ConnectorProps = { name: string; destinationId: string };

const useDestination = () => {
  const createDestinationsImplementation = useFetcher(
    DestinationImplementationResource.createShape()
  );

  const updateDestinationImplementation = useFetcher(
    DestinationImplementationResource.updateShape()
  );

  const recreateDestinationImplementation = useFetcher(
    DestinationImplementationResource.recreateShape()
  );

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
      connector_destination_id: destinationConnector?.destinationId
    });

    try {
      const result = await createDestinationsImplementation(
        {},
        {
          name: values.name,
          destinationId: destinationConnector?.destinationId,
          workspaceId: config.ui.workspaceId,
          connectionConfiguration: values.connectionConfiguration
        },
        [
          [
            DestinationImplementationResource.listShape(),
            { workspaceId: config.ui.workspaceId },
            (
              newDestinationImplementationId: string,
              destinationsImplementationIds: { destinations: string[] }
            ) => ({
              destinations: [
                ...(destinationsImplementationIds?.destinations || []),
                newDestinationImplementationId
              ]
            })
          ]
        ]
      );

      AnalyticsService.track("New Destination - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - success",
        connector_destination: destinationConnector?.name,
        connector_destination_id: destinationConnector?.destinationId
      });

      return result;
    } catch (e) {
      AnalyticsService.track("New Destination - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - failure",
        connector_destination: destinationConnector?.name,
        connector_destination_id: destinationConnector?.destinationId
      });
      throw e;
    }
  };

  const updateDestination = async ({
    values,
    destinationImplementationId
  }: {
    values: ValuesProps;
    destinationImplementationId: string;
  }) => {
    return await updateDestinationImplementation(
      {
        destinationImplementationId
      },
      {
        name: values.name,
        destinationImplementationId,
        connectionConfiguration: values.connectionConfiguration
      }
    );
  };

  const recreateDestination = async ({
    values,
    destinationImplementationId
  }: {
    values: ValuesProps;
    destinationImplementationId: string;
  }) => {
    return await recreateDestinationImplementation(
      {
        destinationImplementationId
      },
      {
        name: values.name,
        destinationImplementationId,
        connectionConfiguration: values.connectionConfiguration,
        workspaceId: config.ui.workspaceId,
        destinationId: values.serviceType
      },
      // Method used only in onboarding.
      // Replace all DestinationImplementation List to new item in UpdateParams (to change id)
      [
        [
          DestinationImplementationResource.listShape(),
          { workspaceId: config.ui.workspaceId },
          (newDestinationImplementationId: string) => ({
            destinations: [newDestinationImplementationId]
          })
        ]
      ]
    );
  };

  return { createDestination, updateDestination, recreateDestination };
};

export default useDestination;
