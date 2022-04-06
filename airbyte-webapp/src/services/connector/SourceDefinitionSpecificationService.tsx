import {
  QueryObserverResult,
  QueryObserverSuccessResult,
  useQuery,
} from "react-query";

import { SourceDefinitionSpecification } from "core/domain/connector";
import { useConfig } from "config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { SourceDefinitionSpecificationService } from "core/domain/connector/SourceDefinitionSpecificationService";
import { isDefined } from "utils/common";
import { SCOPE_WORKSPACE } from "../Scope";

export const sourceDefinitionSpecificationKeys = {
  all: [SCOPE_WORKSPACE, "sourceDefinitionSpecification"] as const,
  detail: (id: string | number) =>
    [...sourceDefinitionSpecificationKeys.all, "details", id] as const,
};

function useGetService(): SourceDefinitionSpecificationService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () =>
      new SourceDefinitionSpecificationService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
}

export const useGetSourceDefinitionSpecification = (
  id: string
): SourceDefinitionSpecification => {
  const service = useGetService();

  return (useQuery(sourceDefinitionSpecificationKeys.detail(id), () =>
    service.get(id)
  ) as QueryObserverSuccessResult<SourceDefinitionSpecification>).data;
};

export const useGetSourceDefinitionSpecificationAsync = (
  id: string | null
): QueryObserverResult<SourceDefinitionSpecification, Error> => {
  const service = useGetService();

  const escapedId = id ?? "";
  return useQuery(
    sourceDefinitionSpecificationKeys.detail(escapedId),
    () => service.get(escapedId),
    {
      suspense: false,
      enabled: isDefined(id),
    }
  );
};
