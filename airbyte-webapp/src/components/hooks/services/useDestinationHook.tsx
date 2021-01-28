import { useCallback } from "react";
import { useFetcher } from "rest-hooks";
import { useStatefulResource } from "@rest-hooks/legacy";

import config from "../../../config";
import DestinationResource, {
  Destination
} from "../../../core/resources/Destination";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import ConnectionResource, {
  Connection
} from "../../../core/resources/Connection";
import { Routes } from "../../../pages/routes";
import useRouter from "../useRouterHook";
import DestinationDefinitionSpecificationResource from "../../../core/resources/DestinationDefinitionSpecification";
import SchedulerResource from "../../../core/resources/Scheduler";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: any;
};

type ConnectorProps = { name: string; destinationDefinitionId: string };

export const useDestinationDefinitionSpecificationLoad = (
  destinationDefinitionId: string
) => {
  const {
    loading: isLoading,
    error,
    data: destinationDefinitionSpecification
  } = useStatefulResource(
    DestinationDefinitionSpecificationResource.detailShape(),
    destinationDefinitionId
      ? {
          destinationDefinitionId
        }
      : undefined
  );

  return { destinationDefinitionSpecification, error, isLoading };
};

const useDestination = () => {
  const { push } = useRouter();

  const createDestinationsImplementation = useFetcher(
    DestinationResource.createShape()
  );

  const destinationCheckConnectionShape = useFetcher(
    SchedulerResource.destinationCheckConnectionShape()
  );

  const updatedestination = useFetcher(
    DestinationResource.partialUpdateShape()
  );

  const recreatedestination = useFetcher(DestinationResource.recreateShape());

  const destinationDelete = useFetcher(DestinationResource.deleteShape());

  const updateConnectionsStore = useFetcher(
    ConnectionResource.updateStoreAfterDeleteShape()
  );

  const createDestination = async ({
    values,
    destinationConnector
  }: {
    values: ValuesProps;
    destinationConnector?: ConnectorProps;
  }) => {
    AnalyticsService.track("New Destination - Action", {
      action: "Test a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id:
        destinationConnector?.destinationDefinitionId
    });

    try {
      await destinationCheckConnectionShape({
        destinationDefinitionId: destinationConnector?.destinationDefinitionId,
        connectionConfiguration: values.connectionConfiguration
      });

      // Try to crete destination
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
              destinations: [
                ...(destinationIds?.destinations || []),
                newdestinationId
              ]
            })
          ]
        ]
      );

      AnalyticsService.track("New Destination - Action", {
        action: "Tested connector - success",
        connector_destination: destinationConnector?.name,
        connector_destination_definition_id:
          destinationConnector?.destinationDefinitionId
      });

      return result;
    } catch (e) {
      AnalyticsService.track("New Destination - Action", {
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
    await destinationCheckConnectionShape({
      connectionConfiguration: values.connectionConfiguration,
      name: values.name,
      destinationId
    });

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

  const checkDestinationConnection = useCallback(
    async ({ destinationId }: { destinationId: string }) => {
      return await destinationCheckConnectionShape({
        destinationId: destinationId
      });
    },
    [destinationCheckConnectionShape]
  );

  const deleteDestination = async ({
    destination,
    connectionsWithDestination
  }: {
    destination: Destination;
    connectionsWithDestination: Connection[];
  }) => {
    await destinationDelete({
      destinationId: destination.destinationId
    });

    // To delete connections with current source from local store
    connectionsWithDestination.map(item =>
      updateConnectionsStore({ connectionId: item.connectionId })
    );

    push(Routes.Destination);
  };

  return {
    createDestination,
    updateDestination,
    recreateDestination,
    deleteDestination,
    checkDestinationConnection
  };
};

export default useDestination;
