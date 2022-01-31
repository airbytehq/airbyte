import { useMemo } from "react";
import { UserService } from "packages/cloud/lib/domain/users";

import { useDefaultRequestMiddlewares } from "packages/cloud/services/useDefaultRequestMiddlewares";
import { useConfig } from "packages/cloud/services/config";

export function useGetUserService(): UserService {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  const { cloudApiUrl } = useConfig();

  return useMemo(() => new UserService(cloudApiUrl, requestAuthMiddleware), [
    cloudApiUrl,
    requestAuthMiddleware,
  ]);
}
