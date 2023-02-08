// This module is for the business logic of working with dbt Cloud webhooks.
// Static config data, urls, functions which wrangle the APIs to manipulate
// records in ways suited to the UI user workflows--all the implementation
// details of working with dbtCloud jobs as webhook operations, all goes here.
// The presentation logic and orchestration in the UI all goes elsewhere.
//
// About that business logic:
// - for now, the code treats "webhook operations" and "dbt Cloud job" as synonymous.
// - custom domains aren't yet supported

import isEmpty from "lodash/isEmpty";
import { useMutation, useQuery } from "react-query";

import { MissingConfigError, useConfig } from "config";
import {
  OperatorType,
  WebBackendConnectionRead,
  OperationRead,
  OperatorWebhookWebhookType,
  WebhookConfigRead,
  WorkspaceRead,
} from "core/request/AirbyteClient";
import { useWebConnectionService } from "hooks/services/useConnectionHook";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import {
  DbtCloudJobInfo,
  webBackendGetAvailableDbtJobsForWorkspace,
  WorkspaceGetDbtJobsResponse,
} from "packages/cloud/lib/domain/dbtCloud/api";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useUpdateWorkspace } from "services/workspaces/WorkspacesService";

export interface DbtCloudJob {
  accountId: number;
  jobId: number;
  operationId?: string;
  jobName?: string;
}
export type { DbtCloudJobInfo } from "packages/cloud/lib/domain/dbtCloud/api";
const webhookConfigName = "dbt cloud";
const jobName = (t: DbtCloudJob) => `${t.accountId}/${t.jobId}`;

const isDbtWebhookConfig = (webhookConfig: WebhookConfigRead) => !!webhookConfig.name?.includes("dbt");

export const toDbtCloudJob = (operationRead: OperationRead): DbtCloudJob => {
  if (operationRead.operatorConfiguration.webhook?.webhookType === "dbtCloud") {
    const dbtCloud = operationRead.operatorConfiguration.webhook.dbtCloud as DbtCloudJob;
    return {
      accountId: dbtCloud.accountId,
      jobId: dbtCloud.jobId,
    };
  }
  throw new Error(
    `Cannot convert operationRead of type ${operationRead.operatorConfiguration.operatorType} to DbtCloudJob`
  );
};

const isDbtCloudJob = (operation: OperationRead): boolean =>
  operation.operatorConfiguration.operatorType === OperatorType.webhook;

export const isSameJob = (remoteJob: DbtCloudJobInfo, savedJob: DbtCloudJob): boolean =>
  savedJob.accountId === remoteJob.accountId && savedJob.jobId === remoteJob.jobId;

type ServiceToken = string;

export const useSubmitDbtCloudIntegrationConfig = () => {
  const { workspaceId } = useCurrentWorkspace();
  const { mutateAsync: updateWorkspace } = useUpdateWorkspace();

  return useMutation<WorkspaceRead, Error, ServiceToken>(
    ["submitWorkspaceDbtCloudToken", workspaceId],
    async (authToken: string) => {
      return await updateWorkspace({
        workspaceId,
        webhookConfigs: [
          {
            name: webhookConfigName,
            authToken,
          },
        ],
      });
    }
  );
};

export const useDbtIntegration = (connection: WebBackendConnectionRead) => {
  const workspace = useCurrentWorkspace();
  const { workspaceId } = workspace;
  const connectionService = useWebConnectionService();

  const hasDbtIntegration = !isEmpty(workspace.webhookConfigs?.filter(isDbtWebhookConfig));
  const webhookConfigId = workspace.webhookConfigs?.find((config) => isDbtWebhookConfig(config))?.id;

  const dbtCloudJobs = [...(connection.operations?.filter((operation) => isDbtCloudJob(operation)) || [])].map(
    toDbtCloudJob
  );
  const otherOperations = [...(connection.operations?.filter((operation) => !isDbtCloudJob(operation)) || [])];

  const { mutateAsync, isLoading } = useMutation({
    mutationFn: (jobs: DbtCloudJob[]) => {
      return connectionService.update({
        connectionId: connection.connectionId,
        operations: [
          ...otherOperations,
          ...jobs.map((job) => ({
            workspaceId,
            ...(job.operationId ? { operationId: job.operationId } : {}),
            name: jobName(job),
            operatorConfiguration: {
              operatorType: OperatorType.webhook,
              webhook: {
                webhookType: OperatorWebhookWebhookType.dbtCloud,
                dbtCloud: {
                  jobId: job.jobId,
                  accountId: job.accountId,
                },
                // if `hasDbtIntegration` is true, webhookConfigId is guaranteed to exist
                ...(webhookConfigId ? { webhookConfigId } : {}),
              },
            },
          })),
        ],
      });
    },
  });

  return {
    hasDbtIntegration,
    dbtCloudJobs,
    saveJobs: mutateAsync,
    isSaving: isLoading,
  };
};

export const useAvailableDbtJobs = () => {
  const { cloudApiUrl } = useConfig();
  if (!cloudApiUrl) {
    throw new MissingConfigError("Missing required configuration cloudApiUrl");
  }

  const config = { apiUrl: cloudApiUrl };
  const middlewares = useDefaultRequestMiddlewares();
  const requestOptions = { config, middlewares };
  const workspace = useCurrentWorkspace();
  const { workspaceId } = workspace;
  const dbtConfigId = workspace.webhookConfigs?.find((config) => config.name?.includes("dbt"))?.id;

  if (!dbtConfigId) {
    throw new Error("cannot request available dbt jobs for a workspace with no dbt cloud integration configured");
  }

  const results = useQuery(
    ["dbtCloud", dbtConfigId, "list"],
    () => webBackendGetAvailableDbtJobsForWorkspace({ workspaceId, dbtConfigId }, requestOptions),
    {
      suspense: true,
    }
  );

  // casting type to remove `| undefined`, since `suspense: true` will ensure the value
  // is, in fact, available
  return (results.data as WorkspaceGetDbtJobsResponse).availableDbtJobs;
};
