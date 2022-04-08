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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  static extractJobInfo(error: any): JobInfo | null {
    if (!error) {
      return null;
    }
    return isLogsRequestError(error) ? error.jobInfo : null;
  }
}

export function isLogsRequestError(error: { __type?: string }): error is LogsRequestError {
  return error.__type === "common.errorWithLogs";
}
