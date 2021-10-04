import { useMutation } from "react-query";

import { useGetUserService } from "./UserService";

export const useUserHook = () => {
  const service = useGetUserService();

  return useMutation(async (payload: { email: string; workspaceId: string }) =>
    service.remove(payload.email, payload.workspaceId)
  );
};
