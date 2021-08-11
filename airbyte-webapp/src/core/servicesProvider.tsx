import { useEffect, useMemo } from "react";
import { useMap } from "react-use";

type Service = any;

type ServicesProvider = {
  register(name: string, rm: Service): void;
  unregister(name: string): void;
  services: Service[];
};

let services: {
  [key: string]: Service;
} = {};

export function getServices() {
  return Object.values(services);
}

export function getService(serviceId: string): Service {
  return services[serviceId];
}

export function registerService(serviceId: string, service: Service): void {
  services[serviceId] = service;
}

/**
 *
 */
export const useServicesProvider = (): ServicesProvider => {
  const [registeredServices, { remove, set }] = useMap<{
    [key: string]: Service;
  }>();

  useEffect(() => {
    services = registeredServices;
  }, [registeredServices]);

  return useMemo<ServicesProvider>(
    () => ({
      services: Object.values(registeredServices),
      register: set,
      unregister: remove,
    }),
    [registeredServices, remove, set]
  );
};
