import { useQuery } from "react-query";

import { useConfig } from "config";
import { DestinationDefinitionSpecificationService } from "core/domain/connector/DestinationDefinitionSpecificationService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { isDefined } from "utils/common";

import { DestinationDefinitionSpecificationRead } from "../../core/request/GeneratedApi";
import { SCOPE_WORKSPACE } from "../Scope";
import { useSuspenseQuery } from "./useSuspenseQuery";

export const destinationDefinitionSpecificationKeys = {
  all: [SCOPE_WORKSPACE, "destinationDefinitionSpecification"] as const,
  detail: (id: string | number) => [...destinationDefinitionSpecificationKeys.all, "details", id] as const,
};

function useGetService(): DestinationDefinitionSpecificationService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new DestinationDefinitionSpecificationService(), [apiUrl, requestAuthMiddleware]);
}

export const useGetDestinationDefinitionSpecification = (id: string): DestinationDefinitionSpecificationRead => {
  const service = useGetService();

  return useSuspenseQuery(destinationDefinitionSpecificationKeys.detail(id), () => service.get(id));
};

export const useGetDestinationDefinitionSpecificationAsync = (id: string | null) => {
  const service = useGetService();

  const escapedId = id ?? "";
  return useQuery(destinationDefinitionSpecificationKeys.detail(escapedId), () => service.get(escapedId), {
    enabled: isDefined(id),
  });
};
