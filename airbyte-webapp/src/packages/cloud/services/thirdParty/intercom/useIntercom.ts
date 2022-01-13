import { useEffect } from "react";
import {
  useIntercom as useIntercomProvider,
  IntercomContextValues,
} from "react-use-intercom";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

export const useIntercom = (): IntercomContextValues => {
  const intercomContextValues = useIntercomProvider();

  // It may be better to get these values from analytics context
  // in case it will be possible to init intercom for non authorized users
  const user = useCurrentUser();
  const workspace = useCurrentWorkspace();

  useEffect(() => {
    intercomContextValues.boot({
      email: user.email,
      name: user.name,
      userId: user.userId,
      userHash: user.intercomHash,

      customAttributes: {
        workspaceId: workspace?.workspaceId,
      },
    });

    return () => intercomContextValues.shutdown();
  }, [user]);

  useEffect(() => {
    intercomContextValues.update({
      customAttributes: {
        workspaceId: workspace?.workspaceId,
      },
    });
  }, [workspace.workspaceId]);

  return intercomContextValues;
};
