import React, { useContext, useEffect, useMemo } from "react";
import { useMap } from "react-use";

type ServiceContainer = {
  [key: string]: Service;
};

type Service = any;

type ServicesProviderApi = {
  register(name: string, service: Service): void;
  getService<T>(serviceType: string): T;
  unregister(name: string): void;
  registeredServices: ServiceContainer;
};

const ServicesProviderContext = React.createContext<ServicesProviderApi | null>(
  null
);

export const ServicesProvider: React.FC<{ inject?: ServiceContainer }> = ({
  children,
  inject,
}) => {
  const [registeredServices, { remove, set }] = useMap<ServiceContainer>(
    inject
  );

  const ctxValue = useMemo<ServicesProviderApi>(
    () => ({
      register: set,
      getService: (serviceType) => registeredServices[serviceType],
      unregister: remove,
      registeredServices,
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
  useInjectServices(serviceInject);

  return <>{children}</>;
};

export const WithService: React.FC<{
  serviceInject: ServiceInject[];
}> = React.memo(WithServiceInner);

export function useInjectServices(serviceInject: ServiceContainer): void {
  const { register, unregister } = useServicesProvider();

  useEffect(() => {
    Object.entries(serviceInject).forEach(([token, service]) =>
      register(token, service)
    );

    return () => Object.keys(serviceInject).forEach(unregister);
  }, [serviceInject]);
}

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
  const { registeredServices } = useServicesProvider();

  return useMemo(() => registeredServices[serviceToken], [
    registeredServices,
    serviceToken,
  ]);
}

// This is workaround for rest-hooks
let services: ServiceContainer = {};

export function getService<T extends Service>(serviceId: string): T {
  return services[serviceId];
}

//
