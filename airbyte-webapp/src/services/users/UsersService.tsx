import { useMutation, useQueryClient } from "react-query";

import { useUser } from "core/AuthContext";
import { UpdateRoleRequestBody } from "core/domain/role";
import { User, UserService, UsersList } from "core/domain/user";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { SCOPE_USER } from "../Scope";
import { useInitService } from "../useInitService";

export const userKeys = {
  all: [SCOPE_USER, "users"] as const,
  list: () => [...userKeys.all, "list"] as const,
};

function useUserService() {
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new UserService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares, removeUser]
  );
}

export const useListUsers = () => {
  const service = useUserService();
  return useSuspenseQuery(userKeys.list(), () => service.list()).data;
};

export const useAddUsers = () => {
  const service = useUserService();
  const queryClient = useQueryClient();

  return useMutation(() => service.add(), {
    onSuccess: (_data) => {
      queryClient.setQueryData(userKeys.list(), (lst: UsersList | undefined) => ({ data: lst?.data } as UsersList));
    },
  });
};

export const useDeleteUser = () => {
  const service = useUserService();
  const queryClient = useQueryClient();

  return useMutation((id: string) => service.delete(id), {
    onSuccess: (_data: any) => {
      queryClient.setQueryData(userKeys.list(), (lst: UsersList | undefined) => {
        const users = lst?.data.filter((user) => user.id !== _data?.data);
        return { data: users } as UsersList;
      });
    },
  });
};

export const useResendInvite = () => {
  const service = useUserService();
  const queryClient = useQueryClient();

  return useMutation((id: string) => service.resendInvite(id), {
    onSuccess: (_data) => {
      queryClient.setQueryData(userKeys.list(), (lst: UsersList | undefined) => ({ data: lst?.data } as UsersList));
    },
  });
};

export const useUpdateRole = () => {
  const service = useUserService();
  const queryClient = useQueryClient();

  return useMutation((UpdateRoleBody: UpdateRoleRequestBody) => service.updateRole(UpdateRoleBody), {
    onSuccess: (_data: any) => {
      queryClient.setQueryData(userKeys.list(), (lst: UsersList | undefined) => {
        const users = lst?.data as User[];
        const userIndex = users.findIndex((user) => user.id === _data.data.id) as number;
        if (userIndex >= 0) {
          users[userIndex].roleIndex = _data.data.roleIndex;
          return { data: users } as UsersList;
        }
        return { data: lst?.data } as UsersList;
      });
    },
  });
};

export const useUserAsyncAction = (): {
  onAddUser: () => Promise<any>;
  onDeleteUser: (id: string) => Promise<any>;
  onResendInvite: (id: string) => Promise<any>;
  onUpdateRole: (UpdateRoleBody: UpdateRoleRequestBody) => Promise<any>;
} => {
  const { mutateAsync: addUsers } = useAddUsers();
  const { mutateAsync: deleteUser } = useDeleteUser();
  const { mutateAsync: resendInvite } = useResendInvite();
  const { mutateAsync: updateRole } = useUpdateRole();

  const onAddUser = async () => {
    return await addUsers();
  };

  const onDeleteUser = async (id: string) => {
    return await deleteUser(id);
  };

  const onResendInvite = async (id: string) => {
    return await resendInvite(id);
  };

  const onUpdateRole = async (UpdateRoleBody: UpdateRoleRequestBody) => {
    return await updateRole(UpdateRoleBody);
  };

  return {
    onAddUser,
    onDeleteUser,
    onResendInvite,
    onUpdateRole,
  };
};
