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
import { useMutation } from "react-query";

import { OperatorType, WebBackendConnectionRead, OperationRead } from "core/request/AirbyteClient";
import { useWebConnectionService } from "hooks/services/useConnectionHook";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useUpdateWorkspace } from "services/workspaces/WorkspacesService";

export interface DbtCloudJob {
  account: string;
  job: string;
  operationId?: string;
}
const dbtCloudDomain = "https://cloud.getdbt.com";
const webhookConfigName = "dbt cloud";
const executionBody = `{"cause": "airbyte"}`;
const jobName = (t: DbtCloudJob) => `${t.account}/${t.job}`;

const toDbtCloudJob = (operation: OperationRead): DbtCloudJob => {
  const { operationId } = operation;
  const { executionUrl } = operation.operatorConfiguration.webhook || {};

  const matches = (executionUrl || "").match(/\/accounts\/([^/]+)\/jobs\/([^]+)\/run\//);

  if (!matches) {
    throw new Error(`Cannot extract dbt cloud job params from executionUrl ${executionUrl}`);
  } else {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [_fullUrl, account, job] = matches;

    return {
      account,
      job,
      operationId,
    };
  }
};
const isDbtCloudJob = (operation: OperationRead): boolean =>
  operation.operatorConfiguration.operatorType === OperatorType.webhook;

export const useSubmitDbtCloudIntegrationConfig = () => {
  const { workspaceId } = useCurrentWorkspace();
  const { mutateAsync: updateWorkspace } = useUpdateWorkspace();

  return useMutation(async (authToken: string) => {
    await updateWorkspace({
      workspaceId,
      webhookConfigs: [
        {
          name: webhookConfigName,
          authToken,
        },
      ],
    });
  });
};

export const useDbtIntegration = (connection: WebBackendConnectionRead) => {
  const workspace = useCurrentWorkspace();
  const { workspaceId } = workspace;
  const connectionService = useWebConnectionService();

  // TODO extract shared isDbtWebhookConfig predicate
  const hasDbtIntegration = !isEmpty(workspace.webhookConfigs?.filter((config) => /dbt/.test(config.name || "")));
  const webhookConfigId = workspace.webhookConfigs?.find((config) => /dbt/.test(config.name || ""))?.id;

  const dbtCloudJobs = [...(connection.operations?.filter((operation) => isDbtCloudJob(operation)) || [])].map(
    toDbtCloudJob
  );
  const otherOperations = [...(connection.operations?.filter((operation) => !isDbtCloudJob(operation)) || [])];

  const saveJobs = (jobs: DbtCloudJob[]) => {
    // TODO dynamically use the workspace's configured dbt cloud domain when it gets returned by backend
    const urlForJob = (job: DbtCloudJob) => `${dbtCloudDomain}/api/v2/accounts/${job.account}/jobs/${job.job}/run/`;

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
              executionUrl: urlForJob(job),
              // if `hasDbtIntegration` is true, webhookConfigId is guaranteed to exist
              ...(webhookConfigId ? { webhookConfigId } : {}),
              executionBody,
            },
          },
        })),
      ],
    });
  };

  return {
    hasDbtIntegration,
    dbtCloudJobs,
    saveJobs,
  };
};
