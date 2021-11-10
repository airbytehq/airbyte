import { useMutation, useQuery, useQueryClient } from "react-query";

import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetUserService } from "./UserService";

export const userKeys = {
  all: ["users"] as const,
  lists: () => [...userKeys.all, "list"] as const,
  list: (filters: string) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, "detail"] as const,
  detail: (id: number) => [...userKeys.details(), id] as const,
};

export const useListUsers = () => {
  const userService = useGetUserService();
  const { workspaceId } = useCurrentWorkspace();

  return useQuery(
    userKeys.list(workspaceId),
    () => userService.listByWorkspaceId(workspaceId),
    { suspense: true }
  );
};

export const useUserHook = () => {
  const service = useGetUserService();
  const queryClient = useQueryClient();

  return {
    removeUserLogic: useMutation(
      async (payload: { email: string; workspaceId: string }) =>
        service.remove(payload.workspaceId, payload.email),
      {
        onSuccess: async () => {
          await queryClient.invalidateQueries(userKeys.lists());
        },
      }
    ),
    inviteUserLogic: useMutation(
      async (payload: {
        users: {
          email: string;
        }[];
        workspaceId: string;
      }) => service.invite(payload.users, payload.workspaceId),
      {
        onSuccess: async () => {
          await queryClient.invalidateQueries(userKeys.lists());
        },
      }
    ),
  };
};
