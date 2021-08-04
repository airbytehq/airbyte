import { useEffect, useMemo } from "react";

import { RequestMiddleware } from "core/request/RequestMiddleware";
import { RequestAuthMiddleware } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { jwtProvider } from "packages/cloud/services/auth/JwtProvider";
import { useRequestMiddlewareProvider } from "core/request/useRequestMiddlewareProvider";

/**
 * This hook is responsible for registering RequestMiddlewares used in BaseRequest
 */
export const useDefaultRequestMiddlewares = (): RequestMiddleware[] => {
  const requestAuthMiddleware = useMemo(
    () => RequestAuthMiddleware(jwtProvider),
    []
  );

  const { register, unregister } = useRequestMiddlewareProvider();

  // This is done only to allow injecting middlewares for static fields of BaseResource
  useEffect(() => {
    register("AuthMiddleware", requestAuthMiddleware);

    return () => unregister("AuthMiddleware");
  }, [register, unregister, requestAuthMiddleware]);

  return useMemo(() => [requestAuthMiddleware], [requestAuthMiddleware]);
};
