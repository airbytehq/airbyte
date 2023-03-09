import { useMutation, useQueryClient } from "react-query";

import { Action, Namespace } from "core/analytics";
import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationService } from "core/domain/connector/DestinationService";
import { useInitService } from "services/useInitService";
import { isDefined } from "utils/common";

import { useAnalyticsService } from "./Analytics";
import { useRemoveConnectionsFromList } from "./useConnectionHook";
import { useCurrentWorkspace } from "./useWorkspace";
import { useConfig } from "../../config";
import { DestinationRead, WebBackendConnectionListItem } from "../../core/request/AirbyteClient";
import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";
import { SCOPE_WORKSPACE } from "../../services/Scope";
import { useDefaultRequestMiddlewares } from "../../services/useDefaultRequestMiddlewares";

export const destinationsKeys = {
  all: [SCOPE_WORKSPACE, "destinations"] as const,
  lists: () => [...destinationsKeys.all, "list"] as const,
  list: (filters: string) => [...destinationsKeys.lists(), { filters }] as const,
  detail: (destinationId: string) => [...destinationsKeys.all, "details", destinationId] as const,
};

interface ValuesProps {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
}

interface ConnectorProps {
  name: string;
  destinationDefinitionId: string;
}

function useDestinationService() {
  const { apiUrl } = useConfig();
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  return useInitService(() => new DestinationService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}

interface DestinationList {
  destinations: DestinationRead[];
}

const useDestinationList = (): DestinationList => {
  const workspace = useCurrentWorkspace();
  const service = useDestinationService();

  return useSuspenseQuery(destinationsKeys.lists(), () => service.list(workspace.workspaceId));
};

const useGetDestination = <T extends string | undefined | null>(
  destinationId: T
): T extends string ? DestinationRead : DestinationRead | undefined => {
  const service = useDestinationService();

  return useSuspenseQuery(destinationsKeys.detail(destinationId ?? ""), () => service.get(destinationId ?? ""), {
    enabled: isDefined(destinationId),
  });
};

const useCreateDestination = () => {
  const service = useDestinationService();
  const queryClient = useQueryClient();
  const workspace = useCurrentWorkspace();

  return useMutation(
    async (createDestinationPayload: { values: ValuesProps; destinationConnector?: ConnectorProps }) => {
      const { values, destinationConnector } = createDestinationPayload;

      if (!destinationConnector?.destinationDefinitionId) {
        throw new Error("No Destination Definition Provided");
      }

      return service.create({
        name: values.name,
        destinationDefinitionId: destinationConnector?.destinationDefinitionId,
        workspaceId: workspace.workspaceId,
        connectionConfiguration: values.connectionConfiguration,
      });
    },
    {
      onSuccess: (data) => {
        queryClient.setQueryData(destinationsKeys.lists(), (lst: DestinationList | undefined) => ({
          destinations: [data, ...(lst?.destinations ?? [])],
        }));
      },
    }
  );
};

const useDeleteDestination = () => {
  const service = useDestinationService();
  const queryClient = useQueryClient();
  const analyticsService = useAnalyticsService();
  const removeConnectionsFromList = useRemoveConnectionsFromList();

  return useMutation(
    (payload: { destination: DestinationRead; connectionsWithDestination: WebBackendConnectionListItem[] }) =>
      service.delete(payload.destination.destinationId),
    {
      onSuccess: (_data, ctx) => {
        analyticsService.track(Namespace.DESTINATION, Action.DELETE, {
          actionDescription: "Destination deleted",
          connector_destination: ctx.destination.destinationName,
          connector_destination_definition_id: ctx.destination.destinationDefinitionId,
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

        const connectionIds = ctx.connectionsWithDestination.map((item) => item.connectionId);
        removeConnectionsFromList(connectionIds);
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
