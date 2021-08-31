import React, { useContext, useEffect, useMemo } from "react";
import { useMap } from "react-use";

import { useConfig } from "config";

import { SourceDefinitionService } from "./domain/connector/SourceDefinitionService";
import { DestinationDefinitionService } from "./domain/connector/DestinationDefinitionService";
import { getMiddlewares } from "./request/useRequestMiddlewareProvider";
import { OperationService } from "./domain/connection";
import { DeploymentService } from "./resources/DeploymentService";

// This is workaround for rest-hooks
let services: {
  [key: string]: Service;
} = {};

export function getService<T extends Service>(serviceId: string): T {
  return services[serviceId];
}

//

type Service = any;

type ServicesProviderApi = {
  register(name: string, service: Service): void;
  getService<T>(serviceType: string): T;
  unregister(name: string): void;
};

const ServicesProviderContext = React.createContext<ServicesProviderApi | null>(
  null
);

export const ServicesProvider: React.FC = ({ children }) => {
  const [registeredServices, { remove, set }] = useMap<{
    [key: string]: Service;
  }>();

  const ctxValue = useMemo<ServicesProviderApi>(
    () => ({
      register: set,
      getService: (serviceType) => registeredServices[serviceType],
      unregister: remove,
    }),
    [registeredServices, remove, set]
  );

  useEffect(() => {
    services = registeredServices;
  }, [registeredServices]);

  return (
    <ServicesProviderContext.Provider value={ctxValue}>
      {children}
    </ServicesProviderContext.Provider>
  );
};

export type ServiceInject = [string, Service];

export const WithService: React.FC<{
  serviceInject: ServiceInject[];
}> = ({ children, serviceInject }) => {
  const { register, unregister } = useServicesProvider();

  useEffect(() => {
    serviceInject.forEach(([token, service]) => {
      register(token, service);
    });

    return () =>
      serviceInject.forEach(([token]) => {
        unregister(token);
      });
  }, [register, unregister, serviceInject]);

  return <>{children}</>;
};

/**
 *
 */
export const useServicesProvider = (): ServicesProviderApi => {
  const diService = useContext(ServicesProviderContext);

  if (!diService) {
    throw new Error(
      "useServicesProvider should be used within ServicesProvider"
    );
  }

  return diService;
};

export function useGetService<T>(serviceToken: string): T {
  const { getService } = useServicesProvider();

  return getService<T>(serviceToken);
}

export let rootUrl = "";

export function useOperationService(): OperationService {
  const config = useConfig();

  return useMemo(() => new OperationService(config.apiUrl, getMiddlewares()), [
    config,
  ]);
}

export const useApiServices = (): void => {
  const config = useConfig();
  const { register, unregister } = useServicesProvider();

  useEffect(() => {
    rootUrl = config.apiUrl;
    register(
      "SourceDefinitionService",
      new SourceDefinitionService(rootUrl, getMiddlewares())
    );
    register(
      "DestinationDefinitionService",
      new DestinationDefinitionService(rootUrl, getMiddlewares())
    );
    register(
      "DeploymentService",
      new DeploymentService(rootUrl, getMiddlewares())
    );

    return () => {
      unregister("SourceDefinitionService");
      unregister("DestinationDefinitionService");
      unregister("DeploymentService");
    };
  }, [config, register, unregister]);
};
