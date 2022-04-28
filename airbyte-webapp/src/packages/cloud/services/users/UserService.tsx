import { useMemo } from "react";

import { UserService } from "packages/cloud/lib/domain/users";
import { useConfig } from "packages/cloud/services/config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

export function useGetUserService(): UserService {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  const { cloudApiUrl } = useConfig();

  return useMemo(() => new UserService(cloudApiUrl, requestAuthMiddleware), [cloudApiUrl, requestAuthMiddleware]);
}
