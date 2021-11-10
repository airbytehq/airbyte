import { useEffect, useMemo } from "react";

import { useConfig } from "config";
import { RequestMiddleware } from "./request/RequestMiddleware";
import { SourceDefinitionService } from "./domain/connector/SourceDefinitionService";
import { DestinationDefinitionService } from "./domain/connector/DestinationDefinitionService";
import { DeploymentService } from "./resources/DeploymentService";
import { OperationService } from "./domain/connection";
import { HealthService } from "./health/HealthService";
import { useGetService, useInjectServices } from "./servicesProvider";

export const useApiServices = (): void => {
  const config = useConfig();
  const middlewares = useGetService<RequestMiddleware[]>(
    "DefaultRequestMiddlewares"
  );

  useEffect(() => {
    window._API_URL = config.apiUrl;
  }, [config]);

  const services = useMemo(
    () => ({
      SourceDefinitionService: new SourceDefinitionService(
        config.apiUrl,
        middlewares
      ),
      DestinationDefinitionService: new DestinationDefinitionService(
        config.apiUrl,
        middlewares
      ),
      DeploymentService: new DeploymentService(config.apiUrl, middlewares),
      OperationService: new OperationService(config.apiUrl, middlewares),
      HealthService: new HealthService(config.apiUrl, middlewares),
    }),
    [config.apiUrl, middlewares]
  );

  useInjectServices(services);
};
