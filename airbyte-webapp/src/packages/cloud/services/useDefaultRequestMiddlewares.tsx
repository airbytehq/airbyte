import { RequestMiddleware } from '@app/core/request/RequestMiddleware';
import { useGetService } from '@app/core/servicesProvider';

/**
 * This hook is responsible for registering RequestMiddlewares used in BaseRequest
 */
export const useDefaultRequestMiddlewares = (): RequestMiddleware[] => {
  return useGetService('DefaultRequestMiddlewares');
};
