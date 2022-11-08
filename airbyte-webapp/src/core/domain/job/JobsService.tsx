import { cancelJob, getJobDebugInfo, getJobInfo, JobListRequestBody, listJobsFor } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class JobsService extends AirbyteRequestService {
  public list(listParams: JobListRequestBody) {
    return listJobsFor(listParams, this.requestOptions);
  }

  public get(id: number) {
    return getJobInfo({ id }, this.requestOptions);
  }

  public cancel(id: number) {
    return cancelJob({ id }, this.requestOptions);
  }

  public getDebugInfo(id: number) {
    return getJobDebugInfo({ id }, this.requestOptions);
  }
}
