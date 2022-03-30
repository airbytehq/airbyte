import { useEffect, useMemo, useRef } from "react";
import { useConfig } from "../config";
import { ConnectionService } from "../core/domain/connection/ConnectionService";
import { useDefaultRequestMiddlewares } from "./useDefaultRequestMiddlewares";
import { DeploymentService } from "../core/domain/deployment/DeploymentService";
import { HealthService } from "../core/health/HealthService";
import { OperationService } from "../core/domain/connection";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useInitService<T extends new (...args: unknown[]) => any>(
  f: () => InstanceType<T>,
  deps: ConstructorParameters<T>
): InstanceType<T> {
  const service = useRef<InstanceType<T> | null>(null);

  useEffect(() => {
    if (service.current !== null) {
      service.current = f();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  if (service.current === null) {
    service.current = f();
  }

  return (service.current as unknown) as InstanceType<T>;
}

function useServices() {
  const config = useConfig();

  const urlRef = useRef<string>(config.apiUrl);
  urlRef.current = config.apiUrl;

  const services = useMemo(
    () => ["ConnectionService", new ConnectionService(() => urlRef.current)],
    []
  );

  return services;
}

function useDeploymentService(): DeploymentService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new DeploymentService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

function useHealthService(): HealthService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new HealthService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

function useOperationService(): OperationService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new OperationService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

export {
  useServices,
  useDeploymentService,
  useOperationService,
  useHealthService,
};
