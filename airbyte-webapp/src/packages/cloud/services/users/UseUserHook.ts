import { useMutation } from "react-query";

import { useGetUserService } from "./UserService";

export const useUserHook = () => {
  const service = useGetUserService();

  return {
    removeUserLogic: useMutation(
      async (payload: { email: string; workspaceId: string }) =>
        service.remove(payload.workspaceId, payload.email)
    ),
  };
};
