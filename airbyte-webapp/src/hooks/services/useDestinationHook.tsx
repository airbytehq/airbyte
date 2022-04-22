import { useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import { Connection, ConnectionConfiguration } from "core/domain/connection";
import { Destination } from "core/domain/connector";
import { DestinationService } from "core/domain/connector/DestinationService";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { isDefined } from "utils/common";

import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";
import { SCOPE_WORKSPACE } from "../../services/Scope";
import { connectionsKeys, ListConnection } from "./useConnectionHook";
import { useCurrentWorkspace } from "./useWorkspace";

export const destinationsKeys = {
  all: [SCOPE_WORKSPACE, "destinations"] as const,
  lists: () => [...destinationsKeys.all, "list"] as const,
  list: (filters: string) => [...destinationsKeys.lists(), { filters }] as const,
  detail: (destinationId: string) => [...destinationsKeys.all, "details", destinationId] as const,
};
//
type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
};
//
type ConnectorProps = { name: string; destinationDefinitionId: string };

function useDestinationService(): DestinationService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new DestinationService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

type DestinationList = { destinations: Destination[] };

const useDestinationList = (): DestinationList => {
  const workspace = useCurrentWorkspace();
  const service = useDestinationService();

  return useSuspenseQuery(destinationsKeys.lists(), () => service.list(workspace.workspaceId));
};

const useGetDestination = <T extends string | undefined | null>(
  destinationId: T
): T extends string ? Destination : Destination | undefined => {
  const service = useDestinationService();

  return useSuspenseQuery(destinationsKeys.detail(destinationId ?? ""), () => service.get(destinationId ?? ""), {
    enabled: isDefined(destinationId),
  });
};

const useCreateDestination = () => {
  const service = useDestinationService();
  const queryClient = useQueryClient();
  const workspace = useCurrentWorkspace();

  const analyticsService = useAnalyticsService();

  return useMutation(
    async (createDestinationPayload: { values: ValuesProps; destinationConnector?: ConnectorProps }) => {
      const { values, destinationConnector } = createDestinationPayload;

      return service.create({
        name: values.name,
        destinationDefinitionId: destinationConnector?.destinationDefinitionId,
        workspaceId: workspace.workspaceId,
        connectionConfiguration: values.connectionConfiguration,
      });
    },
    {
      onSuccess: (data, ctx) => {
        analyticsService.track("New Destination - Action", {
          action: "Tested connector - success",
          connector_destination: ctx.destinationConnector?.name,
          connector_destination_definition_id: ctx.destinationConnector?.destinationDefinitionId,
        });
        queryClient.setQueryData(destinationsKeys.lists(), (lst: DestinationList | undefined) => ({
          destinations: [data, ...(lst?.destinations ?? [])],
        }));
      },
      onError: (_, ctx) => {
        analyticsService.track("New Destination - Action", {
          action: "Tested connector - failure",
          connector_destination: ctx.destinationConnector?.name,
          connector_destination_definition_id: ctx.destinationConnector?.destinationDefinitionId,
        });
      },
    }
  );
};

const useDeleteDestination = () => {
  const service = useDestinationService();
  const queryClient = useQueryClient();
  const analyticsService = useAnalyticsService();

  return useMutation(
    (payload: { destination: Destination; connectionsWithDestination: Connection[] }) =>
      service.delete(payload.destination.destinationId),
    {
      onSuccess: (_data, ctx) => {
        analyticsService.track("Destination - Action", {
          action: "Delete destination",
          connector_destination: ctx.destination.destinationName,
          connector_destination_id: ctx.destination.destinationDefinitionId,
        });

        queryClient.removeQueries(destinationsKeys.detail(ctx.destination.destinationId));
        queryClient.setQueryData(
          destinationsKeys.lists(),
          (lst: DestinationList | undefined) =>
            ({
              destinations:
                lst?.destinations.filter((conn) => conn.destinationId !== ctx.destination.destinationId) ?? [],
            } as DestinationList)
        );

        // To delete connections with current destination from local store
        const connectionIds = ctx.connectionsWithDestination.map((item) => item.connectionId);

        queryClient.setQueryData(connectionsKeys.lists(), (ls: ListConnection | undefined) => ({
          connections: ls?.connections.filter((c) => connectionIds.includes(c.connectionId)) ?? [],
        }));
      },
    }
  );
};

const useUpdateDestination = () => {
  const service = useDestinationService();
  const queryClient = useQueryClient();

  return useMutation(
    (updateDestinationPayload: { values: ValuesProps; destinationId: string }) => {
      return service.update({
        name: updateDestinationPayload.values.name,
        destinationId: updateDestinationPayload.destinationId,
        connectionConfiguration: updateDestinationPayload.values.connectionConfiguration,
      });
    },
    {
      onSuccess: (data) => {
        queryClient.setQueryData(destinationsKeys.detail(data.destinationId), data);
      },
    }
  );
};

export { useDestinationList, useGetDestination, useCreateDestination, useDeleteDestination, useUpdateDestination };
