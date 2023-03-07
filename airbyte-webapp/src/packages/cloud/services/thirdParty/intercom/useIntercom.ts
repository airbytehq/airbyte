import { useEffect } from "react";
import { useIntercom as useIntercomProvider, IntercomContextValues } from "react-use-intercom";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

export const useIntercom = (): IntercomContextValues => {
  const intercomContextValues = useIntercomProvider();

  const user = useCurrentUser();
  const workspaceId = useCurrentWorkspaceId();

  useEffect(() => {
    intercomContextValues.boot({
      email: user.email,
      name: user.name,
      userId: user.userId,
      userHash: user.intercomHash,

      customAttributes: {
        workspace_id: workspaceId,
      },
    });

    return () => intercomContextValues.shutdown();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  useEffect(() => {
    intercomContextValues.update({
      customAttributes: {
        workspace_id: workspaceId,
      },
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  return intercomContextValues;
};
