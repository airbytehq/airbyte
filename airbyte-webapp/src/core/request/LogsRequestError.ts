import { JobWithAttemptsRead } from "./AirbyteClient";
import { CommonRequestError } from "./CommonRequestError";

export class LogsRequestError extends CommonRequestError {
  __type = "common.errorWithLogs";
  jobInfo: JobWithAttemptsRead;

  constructor(jobInfo: JobWithAttemptsRead, response: Response, msg?: string) {
    super(response, msg);
    this.jobInfo = jobInfo;
    this._status = 400;
  }

  static extractJobInfo(error: unknown): JobWithAttemptsRead | null {
    if (!error) {
      return null;
    }
    return isLogsRequestError(error) ? error.jobInfo : null;
  }
}

export function isLogsRequestError(error: unknown): error is LogsRequestError {
  return (error as LogsRequestError).__type === "common.errorWithLogs";
}
