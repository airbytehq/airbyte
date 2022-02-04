import { JobInfo } from "core/domain/job/Job";

import { CommonRequestError } from "./CommonRequestError";

export class LogsRequestError extends CommonRequestError {
  __type = "common.errorWithLogs";
  jobInfo: JobInfo;

  constructor(jobInfo: JobInfo, response: Response, msg?: string) {
    super(response, msg);
    this.jobInfo = jobInfo;
    this._status = 400;
  }

  static extractJobInfo(error: unknown): JobInfo | null {
    if (!error) {
      return null;
    }
    return isLogsRequestError(error) ? error.jobInfo : null;
  }
}

export function isLogsRequestError(error: any): error is LogsRequestError {
  return error.__type === "common.errorWithLogs";
}
