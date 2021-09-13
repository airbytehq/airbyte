import { useMemo } from 'react'
import { UserService } from '@app/packages/cloud/lib/domain/users'

import { useDefaultRequestMiddlewares } from '@app/packages/cloud/services/useDefaultRequestMiddlewares'
import { useConfig } from '@app/packages/cloud/services/config'

export function useGetUserService(): UserService {
  const requestAuthMiddleware = useDefaultRequestMiddlewares()
  const { cloudApiUrl } = useConfig()

  return useMemo(
    () => new UserService(cloudApiUrl, requestAuthMiddleware),
    [cloudApiUrl, requestAuthMiddleware]
  )
}
