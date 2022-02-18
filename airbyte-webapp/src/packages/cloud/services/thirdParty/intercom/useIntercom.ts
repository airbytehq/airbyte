import { useEffect } from "react";
import {
  useIntercom as useIntercomProvider,
  IntercomContextValues,
} from "react-use-intercom";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useAnalytics } from "hooks/services/Analytics";

export const useIntercom = (): IntercomContextValues => {
  const intercomContextValues = useIntercomProvider();

  const user = useCurrentUser();
  const { analyticsContext } = useAnalytics();

  useEffect(() => {
    intercomContextValues.boot({
      email: user.email,
      name: user.name,
      userId: user.userId,
      userHash: user.intercomHash,

      customAttributes: {
        workspace_id: analyticsContext.workspaceId,
      },
    });

    return () => intercomContextValues.shutdown();
  }, [user]);

  useEffect(() => {
    intercomContextValues.update({
      customAttributes: {
        workspace_id: analyticsContext.workspace_id,
      },
    });
  }, [analyticsContext.workspace_id]);

  return intercomContextValues;
};
