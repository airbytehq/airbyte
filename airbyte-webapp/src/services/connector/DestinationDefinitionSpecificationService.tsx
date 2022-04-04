import {
  QueryObserverResult,
  QueryObserverSuccessResult,
  useQuery,
} from "react-query";

import { DestinationDefinitionSpecification } from "core/domain/connector";
import { useConfig } from "config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { DestinationDefinitionSpecificationService } from "core/domain/connector/DestinationDefinitionSpecificationService";
import { isDefined } from "utils/common";
import { SCOPE_WORKSPACE } from "../Scope";

export const destinationDefinitionSpecificationKeys = {
  all: [SCOPE_WORKSPACE, "destinationDefinitionSpecification"] as const,
  detail: (id: string | number) =>
    [...destinationDefinitionSpecificationKeys.all, "details", id] as const,
};

function useGetService(): DestinationDefinitionSpecificationService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () =>
      new DestinationDefinitionSpecificationService(
        apiUrl,
        requestAuthMiddleware
      ),
    [apiUrl, requestAuthMiddleware]
  );
}

export const useGetDestinationDefinitionSpecification = (
  id: string
): DestinationDefinitionSpecification => {
  const service = useGetService();

  return (useQuery(destinationDefinitionSpecificationKeys.detail(id), () =>
    service.get(id)
  ) as QueryObserverSuccessResult<DestinationDefinitionSpecification>).data;
};

export const useGetDestinationDefinitionSpecificationAsync = (
  id: string | null
): QueryObserverResult<DestinationDefinitionSpecification, Error> => {
  const service = useGetService();

  const escapedId = id ?? "";
  return useQuery(
    destinationDefinitionSpecificationKeys.detail(escapedId),
    () => service.get(escapedId),
    {
      suspense: false,
      enabled: isDefined(id),
    }
  );
};
