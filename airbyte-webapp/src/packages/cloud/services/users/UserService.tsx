import { useMemo } from "react";

import { MissingConfigError, useConfig } from "config";
import { UserService } from "packages/cloud/lib/domain/users";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

export function useGetUserService(): UserService {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  const { cloudApiUrl } = useConfig();

  if (!cloudApiUrl) {
    throw new MissingConfigError("Missing required configuration cloudApiUrl");
  }
  return useMemo(() => new UserService(cloudApiUrl, requestAuthMiddleware), [cloudApiUrl, requestAuthMiddleware]);
}
