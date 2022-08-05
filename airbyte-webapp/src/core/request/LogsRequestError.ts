import { CommonRequestError } from "./CommonRequestError";

export class LogsRequestError extends CommonRequestError {
  __type = "common.errorWithLogs";
  jobInfo: any;

  constructor(jobInfo: any, response: Response, msg?: string) {
    super(response, msg);
    this.jobInfo = jobInfo;
    this._status = 400;
  }

  static extractJobInfo(error: any): any {
    if (!error) {
      return false;
    }
    return isLogsRequestError(error) ? error.jobInfo : null;
  }
}

export function isLogsRequestError(error: any): error is LogsRequestError {
  return error.__type === "common.errorWithLogs";
}
