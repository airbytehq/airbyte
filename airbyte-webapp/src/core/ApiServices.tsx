import React, { useMemo } from "react";

import { useConfig } from "config";

import { OperationService } from "./domain/connection";
import { DestinationDefinitionService } from "./domain/connector/DestinationDefinitionService";
import { SourceDefinitionService } from "./domain/connector/SourceDefinitionService";
import { HealthService } from "./health/HealthService";
import { RequestMiddleware } from "./request/RequestMiddleware";
import { useGetService, useInjectServices } from "./servicesProvider";

export const ApiServices: React.FC<React.PropsWithChildren<unknown>> = React.memo(({ children }) => {
  const config = useConfig();
  const middlewares = useGetService<RequestMiddleware[]>("DefaultRequestMiddlewares");

  const services = useMemo(
    () => ({
      SourceDefinitionService: new SourceDefinitionService(config.apiUrl, middlewares),
      DestinationDefinitionService: new DestinationDefinitionService(config.apiUrl, middlewares),
      OperationService: new OperationService(config.apiUrl, middlewares),
      HealthService: new HealthService(config.apiUrl, middlewares),
    }),
    [config.apiUrl, middlewares]
  );

  useInjectServices(services);

  return <>{children}</>;
});
