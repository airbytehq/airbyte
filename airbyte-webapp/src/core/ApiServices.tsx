import React, { useMemo } from "react";

// import { useConfig } from "config";

import { OperationService } from "./domain/connection";
import { DestinationDefinitionService } from "./domain/connector/DestinationDefinitionService";
import { SourceDefinitionService } from "./domain/connector/SourceDefinitionService";
import { HealthService } from "./health/HealthService";
import { RequestMiddleware } from "./request/RequestMiddleware";
import { useGetService, useInjectServices } from "./servicesProvider";

export const ApiServices: React.FC = React.memo(({ children }) => {
  // const config = useConfig();
  const middlewares = useGetService<RequestMiddleware[]>("DefaultRequestMiddlewares");

  const services = useMemo(
    () => ({
      SourceDefinitionService: new SourceDefinitionService(process.env.REACT_APP_API_URL as string, middlewares),
      DestinationDefinitionService: new DestinationDefinitionService(
        process.env.REACT_APP_API_URL as string,
        middlewares
      ),
      OperationService: new OperationService(process.env.REACT_APP_API_URL as string, middlewares),
      HealthService: new HealthService(process.env.REACT_APP_API_URL as string, middlewares),
    }),
    [process.env.REACT_APP_API_URL as string, middlewares]
  );

  useInjectServices(services);

  return <>{children}</>;
});
