import React, { useContext, useEffect, useMemo } from "react";
import { useMap } from "react-use";

type ServiceContainer = Record<string, Service>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Service = any;

interface ServicesProviderApi {
  register(name: string, service: Service): void;
  getService<T>(serviceType: string): T;
  unregister(name: string): void;
  registeredServices: ServiceContainer;
}

const ServicesProviderContext = React.createContext<ServicesProviderApi | null>(null);

export const ServicesProvider: React.FC<React.PropsWithChildren<{ inject?: ServiceContainer }>> = ({
  children,
  inject,
}) => {
  const [registeredServices, { remove, set }] = useMap<ServiceContainer>(inject);

  const ctxValue = useMemo<ServicesProviderApi>(
    () => ({
      register: set,
      getService: (serviceType) => registeredServices[serviceType],
      unregister: remove,
      registeredServices,
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [registeredServices]
  );

  return <ServicesProviderContext.Provider value={ctxValue}>{children}</ServicesProviderContext.Provider>;
};

export function useInjectServices(serviceInject: ServiceContainer): void {
  const { register, unregister } = useServicesProvider();

  useEffect(() => {
    Object.entries(serviceInject).forEach(([token, service]) => register(token, service));

    return () => Object.keys(serviceInject).forEach(unregister);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serviceInject]);
}

/**
 *
 */
export const useServicesProvider = (): ServicesProviderApi => {
  const diService = useContext(ServicesProviderContext);

  if (!diService) {
    throw new Error("useServicesProvider should be used within ServicesProvider");
  }

  return diService;
};

export function useGetService<T>(serviceToken: string): T {
  const { registeredServices } = useServicesProvider();

  return useMemo(() => registeredServices[serviceToken], [registeredServices, serviceToken]);
}
