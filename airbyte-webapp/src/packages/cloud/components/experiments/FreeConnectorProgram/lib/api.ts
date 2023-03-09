import { WorkspaceId } from "core/request/AirbyteClient";
import { apiOverride } from "core/request/apiOverride";

export type WebBackendGetFreeConnectorProgramInfoForWorkspaceResult = NonNullable<
  Awaited<ReturnType<typeof webBackendGetFreeConnectorProgramInfoForWorkspace>>
>;

export interface WorkspaceIdRequestBody {
  workspaceId: WorkspaceId;
}

// eslint-disable-next-line
type SecondParameter<T extends (...args: any) => any> = T extends (config: any, args: infer P) => any ? P : never;

/**
 * @summary Return a summary of Free Connector Program info for the indicated Cloud Workspace
 */
export const webBackendGetFreeConnectorProgramInfoForWorkspace = (
  workspaceIdRequestBody: WorkspaceIdRequestBody,
  options?: SecondParameter<typeof apiOverride>
) => {
  return apiOverride<WorkspaceFreeConnectorProgramInfoResponse>(
    {
      url: `/v1/web_backend/cloud_workspaces/free_connector_program_info`,
      method: "post",
      headers: { "Content-Type": "application/json" },
      data: workspaceIdRequestBody,
    },
    options
  );
};

export interface WorkspaceFreeConnectorProgramInfoResponse {
  hasEligibleConnector: boolean;
  hasPaymentAccountSaved: boolean;
}
