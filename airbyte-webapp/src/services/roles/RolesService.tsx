import { useUser } from "core/AuthContext";
import { Role, RoleService } from "core/domain/role";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { SCOPE_USER } from "../Scope";
import { useInitService } from "../useInitService";

export const roleKeys = {
  all: [SCOPE_USER, "roles"] as const,
  list: () => [...roleKeys.all, "list"] as const,
};

function useRoleApiService() {
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new RoleService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares, removeUser]
  );
}

export const useListRoles = () => {
  const service = useRoleApiService();
  return useSuspenseQuery(roleKeys.list(), () => service.list()).data;
};

export const useRoleOptions = () => {
  const roles = useListRoles();
  return roles.map((role: Role) => ({ label: role.desc, value: role.index }));
};
