// This module is for the business logic of working with dbt Cloud webhooks.
// Static config data, urls, functions which wrangle the APIs to manipulate
// records in ways suited to the UI user workflows--all the implementation
// details of working with dbtCloud jobs as webhook operations, all goes here.
// The presentation logic and orchestration in the UI all goes elsewhere.

import isEmpty from "lodash/isEmpty";

import {
  /* webBackendUpdateConnection, */
  WebBackendConnectionUpdate,
  OperatorType,
} from "core/request/AirbyteClient";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

export interface DbtCloudJob {
  // TODO rename project->account
  project: string;
  job: string;
}

const webhookConfigName = "dbt cloud";
const executionBody = `{"cause": "airbyte"}`;
const jobName = (t: DbtCloudJob) => `${t.project}/${t.job}`;

const updateConnection = (obj: WebBackendConnectionUpdate) => console.info(`updating with`, obj);

// saves jobs for the current connection
export const useSaveJobsFn = () => {
  const { workspaceId } = useCurrentWorkspace();

  // TODO dynamically use the workspace's configured dbt cloud domain
  const dbtCloudDomain = "https://cloud.getdbt.com";
  const urlForJob = (job: DbtCloudJob) => `${dbtCloudDomain}/api/v2/accounts/${job.project}/jobs/${job.job}`;

  return (jobs: DbtCloudJob[]) =>
    // TODO query and add the actual connectionId and operationId values
    updateConnection({
      connectionId: workspaceId, // lmao I know, right?
      operations: [
        // TODO include all non-dbt-cloud operations in the payload
        ...jobs.map((job) => ({
          workspaceId,
          name: jobName(job),
          // TODO add `operationId` if present
          operatorConfiguration: {
            operatorType: OperatorType.webhook,
            webhook: {
              executionUrl: urlForJob(job),
              webhookConfigName,
              executionBody,
            },
          },
        })),
      ],
    });
};

export const useDbtIntegration = () => {
  const workspace = useCurrentWorkspace();

  return { hasDbtIntegration: !isEmpty(workspace.webhookConfigs) };
};
