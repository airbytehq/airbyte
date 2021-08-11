import { useEffect, useMemo } from "react";
import { useMap } from "react-use";
import { RequestMiddleware } from "./RequestMiddleware";

type RequestMiddlewareProvider = {
  register(name: string, rm: RequestMiddleware): void;
  unregister(name: string): void;
  middlewares: RequestMiddleware[];
};

let middlewares: {
  [key: string]: RequestMiddleware;
} = {};

export function getMiddlewares() {
  console.log(middlewares);
  return Object.values(middlewares);
}

/**
 *
 */
export const useRequestMiddlewareProvider = (): RequestMiddlewareProvider => {
  const [requestMiddlewares, { remove, set }] = useMap<{
    [key: string]: RequestMiddleware;
  }>();

  useEffect(() => {
    middlewares = { ...middlewares, ...requestMiddlewares };
  }, [requestMiddlewares]);

  return useMemo<RequestMiddlewareProvider>(
    () => ({
      middlewares: Object.values(requestMiddlewares),
      register: set,
      unregister: remove,
    }),
    [requestMiddlewares, remove, set]
  );
};
