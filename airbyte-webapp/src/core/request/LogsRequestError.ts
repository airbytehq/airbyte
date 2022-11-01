import { SynchronousJobRead } from "./AirbyteClient";
import { CommonRequestError } from "./CommonRequestError";

export class LogsRequestError extends CommonRequestError {
  __type = "common.errorWithLogs";

  constructor(private jobInfo: SynchronousJobRead, msg?: string) {
    super(undefined, msg);
    this._status = 400;
  }

  static extractJobInfo(error: unknown) {
    if (!error) {
      return null;
    }
    return isLogsRequestError(error) ? error.jobInfo : null;
  }
}

export function isLogsRequestError(error: unknown): error is LogsRequestError {
  return (error as LogsRequestError).__type === "common.errorWithLogs";
}
