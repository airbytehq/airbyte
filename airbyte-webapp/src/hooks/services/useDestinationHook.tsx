import { useCallback } from "react";
import { useFetcher, useResource } from "rest-hooks";
import { useStatefulResource } from "@rest-hooks/legacy";

import DestinationResource, { Destination } from "core/resources/Destination";
import ConnectionResource, { Connection } from "core/resources/Connection";
import { Routes } from "pages/routes";
import useRouter from "../useRouter";
import DestinationDefinitionSpecificationResource, {
  DestinationDefinitionSpecification,
} from "core/resources/DestinationDefinitionSpecification";
import SchedulerResource, { Scheduler } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";
import useWorkspace from "./useWorkspace";
import { useAnalytics } from "hooks/useAnalytics";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
};

type ConnectorProps = { name: string; destinationDefinitionId: string };

export const useDestinationDefinitionSpecificationLoad = (
  destinationDefinitionId: string | null
): {
  isLoading: boolean;
  destinationDefinitionSpecification?: DestinationDefinitionSpecification;
  error?: Error;
} => {
  const {
    loading: isLoading,
    error,
    data: destinationDefinitionSpecification,
  } = useStatefulResource(
    DestinationDefinitionSpecificationResource.detailShape(),
    destinationDefinitionId
      ? {
          destinationDefinitionId,
        }
      : null
  );

  return { destinationDefinitionSpecification, error, isLoading };
};

export const useDestinationDefinitionSpecificationLoadAsync = (
  destinationDefinitionId: string
): DestinationDefinitionSpecification => {
  const definition = useResource(
    DestinationDefinitionSpecificationResource.detailShape(),
    {
      destinationDefinitionId,
    }
  );

  return definition;
};

type DestinationService = {
  checkDestinationConnection: ({
    destinationId,
    values,
  }: {
    destinationId: string;
    values?: ValuesProps;
  }) => Promise<Scheduler>;
  updateDestination: ({
    values,
    destinationId,
  }: {
    values: ValuesProps;
    destinationId: string;
  }) => Promise<Destination>;
  createDestination: ({
    values,
    destinationConnector,
  }: {
    values: ValuesProps;
    destinationConnector?: ConnectorProps;
  }) => Promise<Destination>;
  recreateDestination: ({
    values,
    destinationId,
  }: {
    values: ValuesProps;
    destinationId: string;
  }) => Promise<Destination>;
  deleteDestination: ({
    destination,
    connectionsWithDestination,
  }: {
    destination: Destination;
    connectionsWithDestination: Connection[];
  }) => Promise<void>;
};

const useDestination = (): DestinationService => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const analyticsService = useAnalytics();
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
    destinationConnector,
  }: {
    values: ValuesProps;
    destinationConnector?: ConnectorProps;
  }) => {
    analyticsService.track("New Destination - Action", {
      action: "Test a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id:
        destinationConnector?.destinationDefinitionId,
    });

    try {
      await destinationCheckConnectionShape({
        destinationDefinitionId: destinationConnector?.destinationDefinitionId,
        connectionConfiguration: values.connectionConfiguration,
      });

      // Try to crete destination
      const result = await createDestinationsImplementation(
        {},
        {
          name: values.name,
          destinationDefinitionId:
            destinationConnector?.destinationDefinitionId,
          workspaceId: workspace.workspaceId,
          connectionConfiguration: values.connectionConfiguration,
        },
        [
          [
            DestinationResource.listShape(),
            { workspaceId: workspace.workspaceId },
            (
              newdestinationId: string,
              destinationIds: { destinations: string[] }
            ) => ({
              destinations: [
                ...(destinationIds?.destinations || []),
                newdestinationId,
              ],
            }),
          ],
        ]
      );

      analyticsService.track("New Destination - Action", {
        action: "Tested connector - success",
        connector_destination: destinationConnector?.name,
        connector_destination_definition_id:
          destinationConnector?.destinationDefinitionId,
      });

      return result;
    } catch (e) {
      analyticsService.track("New Destination - Action", {
        action: "Tested connector - failure",
        connector_destination: destinationConnector?.name,
        connector_destination_definition_id:
          destinationConnector?.destinationDefinitionId,
      });
      throw e;
    }
  };

  const updateDestination = async ({
    values,
    destinationId,
  }: {
    values: ValuesProps;
    destinationId: string;
  }) => {
    await destinationCheckConnectionShape({
      connectionConfiguration: values.connectionConfiguration,
      name: values.name,
      destinationId,
    });

    return await updatedestination(
      {
        destinationId,
      },
      {
        name: values.name,
        destinationId,
        connectionConfiguration: values.connectionConfiguration,
      }
    );
  };

  const recreateDestination = async ({
    values,
    destinationId,
  }: {
    values: ValuesProps;
    destinationId: string;
  }) => {
    return await recreatedestination(
      {
        destinationId,
      },
      {
        name: values.name,
        destinationId,
        connectionConfiguration: values.connectionConfiguration,
        workspaceId: workspace.workspaceId,
        destinationDefinitionId: values.serviceType,
      },
      // Method used only in onboarding.
      // Replace all destination List to new item in UpdateParams (to change id)
      [
        [
          DestinationResource.listShape(),
          { workspaceId: workspace.workspaceId },
          (newdestinationId: string) => ({
            destinations: [newdestinationId],
          }),
        ],
      ]
    );
  };

  const checkDestinationConnection = useCallback(
    async ({
      destinationId,
      values,
    }: {
      destinationId: string;
      values?: ValuesProps;
    }) => {
      if (values) {
        return await destinationCheckConnectionShape({
          connectionConfiguration: values.connectionConfiguration,
          name: values.name,
          destinationId: destinationId,
        });
      }
      return await destinationCheckConnectionShape({
        destinationId: destinationId,
      });
    },
    [destinationCheckConnectionShape]
  );

  const deleteDestination = async ({
    destination,
    connectionsWithDestination,
  }: {
    destination: Destination;
    connectionsWithDestination: Connection[];
  }) => {
    await destinationDelete({
      destinationId: destination.destinationId,
    });

    // To delete connections with current source from local store
    connectionsWithDestination.map((item) =>
      updateConnectionsStore({ connectionId: item.connectionId }, undefined)
    );

    push(Routes.Destination);
  };

  return {
    createDestination,
    updateDestination,
    recreateDestination,
    deleteDestination,
    checkDestinationConnection,
  };
};

const useDestinationList = (): { destinations: Destination[] } => {
  const { workspace } = useWorkspace();
  return useResource(DestinationResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useDestinationList };
export default useDestination;
