import { useEffect } from "react";

import { useConfig } from "config";
import { useUser } from "core/AuthContext";
import { useGetService } from "core/servicesProvider";
import { AuthService } from "services/auth/AuthService";

function useUserDetailPoll(): void {
  const { userDetailInterval } = useConfig();
  const authService = useGetService<AuthService>("AuthService");
  const { updateUserRole } = useUser();

  useEffect(() => {
    const userInterval = setInterval(async () => {
      try {
        const user: any = await authService.userInfo();
        const { data } = user;
        updateUserRole?.(data?.role);
      } catch (e) {
        console.log(e);
      }
    }, userDetailInterval);

    return () => clearInterval(userInterval);
  }, [userDetailInterval, authService, updateUserRole]);
}

export { useUserDetailPoll };
