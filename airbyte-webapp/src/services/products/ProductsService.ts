import { useUser } from "core/AuthContext";
import { ProductService } from "core/domain/product";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { SCOPE_USER } from "../Scope";
import { useInitService } from "../useInitService";

export const productKeys = {
  all: [SCOPE_USER, "products"] as const,
  lists: () => [...productKeys.all, "list"] as const,
};

function useProductApiService() {
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new ProductService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares, removeUser]
  );
}

export const useListProducts = () => {
  const service = useProductApiService();

  return useSuspenseQuery(productKeys.lists(), () => service.list()).products;
};
