import React, { useContext, useEffect, useMemo } from "react";
import { useMap } from "react-use";

import { useConfig } from "config";

import { SourceDefinitionService } from "./domain/connector/SourceDefinitionService";
import { DestinationDefinitionService } from "./domain/connector/DestinationDefinitionService";
import { getMiddlewares } from "./request/useRequestMiddlewareProvider";
import { OperationService } from "./domain/connection";
import { DeploymentService } from "./resources/DeploymentService";
import { HealthService } from "./health/HealthService";

type ServiceContainer = {
  [key: string]: Service;
};

type Service = any;

type ServicesProviderApi = {
  register(name: string, service: Service): void;
  registerAll(newMap: ServiceContainer): void;
  getService<T>(serviceType: string): T;
  unregister(name: string): void;
};

const ServicesProviderContext = React.createContext<ServicesProviderApi | null>(
  null
);

export const ServicesProvider: React.FC<{ inject?: ServiceContainer }> = ({
  children,
  inject,
}) => {
  const [
    registeredServices,
    { remove, set, setAll },
  ] = useMap<ServiceContainer>(inject);

  const ctxValue = useMemo<ServicesProviderApi>(
    () => ({
      register: set,
      registerAll: (newServices) =>
        setAll({ ...registeredServices, ...newServices }),
      getService: (serviceType) => registeredServices[serviceType],
      unregister: remove,
    }),
    [registeredServices]
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

const WithServiceInner: React.FC<{
  serviceInject: ServiceInject[];
}> = ({ children, serviceInject }) => {
  const { register, unregister } = useServicesProvider();

  useEffect(() => {
    serviceInject.forEach(([token, service]) => register(token, service));

    return () => serviceInject.forEach(([token]) => unregister(token));
  }, [register, unregister, serviceInject]);

  return <>{children}</>;
};

export const WithService = React.memo(WithServiceInner);

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

// This is workaround for rest-hooks
let services: ServiceContainer = {};

export function getService<T extends Service>(serviceId: string): T {
  return services[serviceId];
}

//

export const useApiServices = (): void => {
  const config = useConfig();
  const { registerAll, unregister } = useServicesProvider();

  useEffect(() => {
    window._API_URL = config.apiUrl;
  }, [config]);

  useEffect(() => {
    const middlewares = getMiddlewares();
    const services = {
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
    };

    registerAll(services);

    return () => Object.keys(services).forEach(unregister);
  }, [config]);
};
