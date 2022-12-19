import { useMemo } from "react";

import { useUser } from "core/AuthContext";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { SCOPE_USER } from "services/Scope";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

import { AuthService } from "./AuthService";

export const authKeys = {
  all: [SCOPE_USER, "auth"] as const,
  userInfo: () => [...authKeys.all, "userInfo"] as const,
};

export const useAuthenticationService = (): AuthService => {
  return useMemo(() => new AuthService(process.env.REACT_APP_API_URL as string), []);
};

function useAuthInitiatedService() {
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new AuthService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares, removeUser]
  );
}

export const useAuthDetail = () => {
  const service = useAuthInitiatedService();
  return useSuspenseQuery(authKeys.userInfo(), () => service.userInfo()).data;
};
