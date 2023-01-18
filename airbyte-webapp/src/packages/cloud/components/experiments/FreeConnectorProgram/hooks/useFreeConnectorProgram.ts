import { useQuery } from "react-query";

import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useConfig } from "packages/cloud/services/config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { webBackendGetFreeConnectorProgramInfoForWorkspace } from "../lib/api";

export const useFreeConnectorProgramInfo = () => {
  const workspaceId = useCurrentWorkspaceId();
  const { cloudApiUrl } = useConfig();
  const config = { apiUrl: cloudApiUrl };
  const middlewares = useDefaultRequestMiddlewares();
  const requestOptions = { config, middlewares };
  const { emailVerified } = useAuthService();

  return useQuery(["freeConnectorProgramInfo", workspaceId], () =>
    webBackendGetFreeConnectorProgramInfoForWorkspace({ workspaceId }, requestOptions).then(
      ({ hasEligibleConnector, hasPaymentAccountSaved }) => {
        const showEnrollmentUi = !hasPaymentAccountSaved && hasEligibleConnector;
        const needsEmailVerification: boolean = emailVerified;

        return { showEnrollmentUi, needsEmailVerification };
      }
    )
  );
};
