import { useMemo } from "react";
import { UserService } from "packages/cloud/lib/domain/users";
import { api } from "packages/cloud/config/api";

import { useDefaultRequestMiddlewares } from "packages/cloud/services/useDefaultRequestMiddlewares";

export function useGetUserService() {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useMemo(() => new UserService(requestAuthMiddleware, api.cloud), [
    requestAuthMiddleware,
  ]);
}
