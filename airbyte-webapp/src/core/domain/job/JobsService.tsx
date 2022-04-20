import { cancelJob, getJobDebugInfo, getJobInfo, JobListRequestBody, listJobsFor } from "../../request/GeneratedApi";

export class JobsService {
  public async list(listParams: JobListRequestBody) {
    return listJobsFor(listParams);
  }

  public async get(id: number) {
    return getJobInfo({ id });
  }

  public async cancel(id: number) {
    return cancelJob({ id });
  }

  public async getDebugInfo(id: number) {
    return getJobDebugInfo({ id });
  }
}
