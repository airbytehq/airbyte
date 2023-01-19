import { useQuery } from "react-query";

import { useExperiment } from "hooks/services/Experiment";
import { useConfig } from "packages/cloud/services/config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { webBackendGetFreeConnectorProgramInfoForWorkspace } from "../lib/api";

export const STRIPE_SUCCESS_QUERY = "fcpEnrollmentSuccess";

export const useFreeConnectorProgram = () => {
  const workspaceId = useCurrentWorkspaceId();
  const { cloudApiUrl } = useConfig();
  const config = { apiUrl: cloudApiUrl };
  const middlewares = useDefaultRequestMiddlewares();
  const requestOptions = { config, middlewares };
  const freeConnectorProgramEnabled = useExperiment("workspace.freeConnectorsProgram.visible", false);

  return useQuery(["freeConnectorProgramInfo", workspaceId], () =>
    webBackendGetFreeConnectorProgramInfoForWorkspace({ workspaceId }, requestOptions).then(
      ({ hasEligibleConnector, hasPaymentAccountSaved }) => {
        const userIsEligibleToEnroll = !hasPaymentAccountSaved && hasEligibleConnector;

        return {
          showEnrollmentUi: freeConnectorProgramEnabled && userIsEligibleToEnroll,
          isEnrolled: freeConnectorProgramEnabled && hasPaymentAccountSaved,
        };
      }
    )
  );
};
