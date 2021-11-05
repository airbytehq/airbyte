import { RequestMiddleware } from "core/request/RequestMiddleware";
import { useGetService } from "core/servicesProvider";

/**
 * This hook is responsible for registering RequestMiddlewares used in BaseRequest
 */
export const useDefaultRequestMiddlewares = (): RequestMiddleware[] => {
  return useGetService<RequestMiddleware[]>("DefaultRequestMiddlewares");
};
