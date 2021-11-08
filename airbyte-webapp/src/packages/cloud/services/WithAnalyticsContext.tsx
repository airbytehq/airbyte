import React, { useEffect } from "react";

import { useAnalyticsCtx } from "hooks/useAnalytics";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

import { useAuthService } from "./auth/AuthService";

const WithAnalyticsContext: React.FC = ({ children }) => {
  const ctx = useAnalyticsCtx();

  const { workspaceId } = useCurrentWorkspace();
  const { user } = useAuthService();

  useEffect(() => {
    ctx.setContext({ workspaceId, userId: user?.userId });

    return () => ctx.removeContextProps(["workspaceId", "userId"]);
  }, [ctx, workspaceId, user?.userId]);

  return <>{children}</>;
};

export default WithAnalyticsContext;
