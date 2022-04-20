import { CommonRequestError } from "./CommonRequestError";
import { JobWithAttemptsRead } from "./GeneratedApi";

export class LogsRequestError extends CommonRequestError {
  __type = "common.errorWithLogs";
  jobInfo: JobWithAttemptsRead;

  constructor(jobInfo: JobWithAttemptsRead, response: Response, msg?: string) {
    super(response, msg);
    this.jobInfo = jobInfo;
    this._status = 400;
  }

  static extractJobInfo(error: any): JobWithAttemptsRead | null {
    if (!error) {
      return null;
    }
    return isLogsRequestError(error) ? error.jobInfo : null;
  }
}

export function isLogsRequestError(error: { __type?: string }): error is LogsRequestError {
  return error.__type === "common.errorWithLogs";
}
