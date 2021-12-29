import { useEffect } from "react";
import { useIntercom as useIntercomProvider } from "react-use-intercom";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";

export const useIntercom = (): void => {
  const user = useCurrentUser();
  const { boot, shutdown } = useIntercomProvider();

  useEffect(() => {
    boot({
      email: user.email,
      name: user.name,
      userId: user.userId,
      userHash: user.intercomHash,
    });

    return () => shutdown();
  }, [user]);
};
