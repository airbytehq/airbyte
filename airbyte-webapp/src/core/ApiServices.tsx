import React, { useMemo } from "react";

// import { useConfig } from "config";
import { useUser } from "core/AuthContext";
import { AuthService } from "services/auth/AuthService";

import { OperationService } from "./domain/connection";
import { DestinationDefinitionService } from "./domain/connector/DestinationDefinitionService";
import { SourceDefinitionService } from "./domain/connector/SourceDefinitionService";
import { HealthService } from "./health/HealthService";
import { RequestMiddleware } from "./request/RequestMiddleware";
import { useGetService, useInjectServices } from "./servicesProvider";

export const ApiServices: React.FC = React.memo(({ children }) => {
  // const config = useConfig();
  const { removeUser } = useUser();
  const middlewares = useGetService<RequestMiddleware[]>("DefaultRequestMiddlewares");

  const services = useMemo(
    () => ({
      SourceDefinitionService: new SourceDefinitionService(
        process.env.REACT_APP_API_URL as string,
        middlewares,
        removeUser
      ),
      DestinationDefinitionService: new DestinationDefinitionService(
        process.env.REACT_APP_API_URL as string,
        middlewares,
        removeUser
      ),
      OperationService: new OperationService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
      HealthService: new HealthService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
      AuthService: new AuthService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    }),
    [process.env.REACT_APP_API_URL as string, middlewares]
  );

  useInjectServices(services);

  return <>{children}</>;
});
