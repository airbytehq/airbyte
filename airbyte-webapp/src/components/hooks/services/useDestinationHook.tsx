import { useFetcher } from "rest-hooks";

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
import { useEffect, useState } from "react";
import DestinationDefinitionSpecificationResource, {
  DestinationDefinitionSpecification
} from "../../../core/resources/DestinationDefinitionSpecification";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: any;
};

type ConnectorProps = { name: string; destinationDefinitionId: string };

export const useDestinationDefinitionSpecificationLoad = (
  destinationDefinitionId: string
) => {
  const [
    destinationDefinitionSpecification,
    setDestinationSpecification
  ] = useState<null | DestinationDefinitionSpecification>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDestinationDefinitionSpecification = useFetcher(
    DestinationDefinitionSpecificationResource.detailShape(),
    true
  );

  useEffect(() => {
    (async () => {
      if (destinationDefinitionId) {
        setIsLoading(true);
        setDestinationSpecification(
          await fetchDestinationDefinitionSpecification({
            destinationDefinitionId
          })
        );
        setIsLoading(false);
      }
    })();
  }, [fetchDestinationDefinitionSpecification, destinationDefinitionId]);

  return { destinationDefinitionSpecification, isLoading };
};

const useDestination = () => {
  const { push } = useRouter();

  const createDestinationsImplementation = useFetcher(
    DestinationResource.createShape()
  );

  const updatedestination = useFetcher(DestinationResource.updateShape());

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
    deleteDestination
  };
};

export default useDestination;
