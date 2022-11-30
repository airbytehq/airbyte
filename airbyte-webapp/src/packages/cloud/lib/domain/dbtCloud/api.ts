import { apiOverride } from "core/request/apiOverride";

/**
 * Get the available dbt Cloud jobs associated with the given workspace config.
 */
export interface WorkspaceGetDbtJobsRequest {
  workspaceId: WorkspaceId;
  /** The config id associated with the dbt Cloud config, references the webhookConfigId in the core API. */
  dbtConfigId: string;
}

/**
 * The available dbt Cloud jobs for the requested workspace config
 */
export interface WorkspaceGetDbtJobsResponse {
  availableDbtJobs: DbtCloudJobInfo[];
}

/**
 * A dbt Cloud job
 */
export interface DbtCloudJobInfo {
  /** The account id associated with the job */
  accountId: number;
  /** The the specific job id returned by the dbt Cloud API */
  jobId: number;
  /** The human-readable name of the job returned by the dbt Cloud API */
  jobName: string;
}

/**
 * @summary Calls the dbt Cloud `List Accounts` and `List jobs` APIs to get the list of available jobs for the dbt auth token associated with the requested workspace config.
 */
export const webBackendGetAvailableDbtJobsForWorkspace = (
  workspaceGetDbtJobsRequest: WorkspaceGetDbtJobsRequest,
  options?: SecondParameter<typeof apiOverride>
) => {
  return apiOverride<WorkspaceGetDbtJobsResponse>(
    {
      url: `/v1/web_backend/cloud_workspaces/get_available_dbt_jobs`,
      method: "post",
      headers: { "Content-Type": "application/json" },
      data: workspaceGetDbtJobsRequest,
    },
    options
  );
};

/**
 * Workspace Id from OSS Airbyte instance
 */
export type WorkspaceId = string;

// eslint-disable-next-line
type SecondParameter<T extends (...args: any) => any> = T extends (config: any, args: infer P) => any ? P : never;
