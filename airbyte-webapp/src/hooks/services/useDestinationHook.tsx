import { useFetcher, useResource } from "rest-hooks";
import { useQueryClient } from "react-query";

import DestinationResource from "core/resources/Destination";
import { Connection } from "core/domain/connection";
import useRouter from "../useRouter";
import { ConnectionConfiguration } from "core/domain/connection";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { Destination } from "core/domain/connector";
import { RoutePaths } from "../../pages/routePaths";
import { connectionsKeys, ListConnection } from "./useConnectionHook";
import { useCurrentWorkspace } from "./useWorkspace";

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
};

type ConnectorProps = { name: string; destinationDefinitionId: string };

type DestinationServiceApi = {
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
  deleteDestination: ({
    destination,
    connectionsWithDestination,
  }: {
    destination: Destination;
    connectionsWithDestination: Connection[];
  }) => Promise<void>;
};

const useDestination = (): DestinationServiceApi => {
  const { push } = useRouter();
  const workspace = useCurrentWorkspace();
  const analyticsService = useAnalyticsService();
  const createDestinationsImplementation = useFetcher(
    DestinationResource.createShape()
  );

  const updatedestination = useFetcher(
    DestinationResource.partialUpdateShape()
  );

  const destinationDelete = useFetcher(DestinationResource.deleteShape());

  const queryClient = useQueryClient();

  const createDestination: DestinationServiceApi["createDestination"] = async ({
    values,
    destinationConnector,
  }) => {
    try {
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

  const updateDestination: DestinationServiceApi["updateDestination"] = async ({
    values,
    destinationId,
  }) =>
    await updatedestination(
      {
        destinationId,
      },
      {
        name: values.name,
        destinationId,
        connectionConfiguration: values.connectionConfiguration,
      }
    );

  const deleteDestination: DestinationServiceApi["deleteDestination"] = async ({
    destination,
    connectionsWithDestination,
  }) => {
    await destinationDelete({
      destinationId: destination.destinationId,
    });

    // To delete connections with current destination from local store
    const connectionIds = connectionsWithDestination.map(
      (item) => item.connectionId
    );

    queryClient.setQueryData(
      connectionsKeys.lists(),
      (ls: ListConnection | undefined) => ({
        connections:
          ls?.connections.filter((c) =>
            connectionIds.includes(c.connectionId)
          ) ?? [],
      })
    );

    push(RoutePaths.Destination);
  };

  return {
    createDestination,
    updateDestination,
    deleteDestination,
  };
};

const useDestinationList = (): { destinations: Destination[] } => {
  const workspace = useCurrentWorkspace();
  return useResource(DestinationResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useDestinationList };
export default useDestination;
