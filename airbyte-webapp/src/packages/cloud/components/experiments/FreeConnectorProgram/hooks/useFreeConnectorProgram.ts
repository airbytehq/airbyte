import { useQuery } from "react-query";

import { useExperiment } from "hooks/services/Experiment";
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
  const freeConnectorProgramEnabled = useExperiment("workspace.freeConnectorsProgram.visible", false);

  return useQuery(["freeConnectorProgramInfo", workspaceId], () =>
    webBackendGetFreeConnectorProgramInfoForWorkspace({ workspaceId }, requestOptions).then(
      ({ hasEligibleConnector, hasPaymentAccountSaved }) => {
        const showEnrollmentUi = !hasPaymentAccountSaved && hasEligibleConnector && freeConnectorProgramEnabled;
        // TODO hardcoding this value to allow testing while data source gets sorted out
        const needsEmailVerification = false;

        return { showEnrollmentUi, needsEmailVerification };
      }
    )
  );
};
