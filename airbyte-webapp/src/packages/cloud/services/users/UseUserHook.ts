import { useMutation } from "react-query";

import { useGetUserService } from "./UserService";

export const useUserHook = (onSuccess: () => void, onError: () => void) => {
  const service = useGetUserService();

  return useMutation(async (id: string) => service.remove(id), {
    onSuccess,
    onError,
  });
};
