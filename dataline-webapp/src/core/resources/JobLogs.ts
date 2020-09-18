import BaseResource from "./BaseResource";

export interface JobLogs {
  logLines: string[];
}

export default class JobLogsResource extends BaseResource implements JobLogs {
  readonly logLines: string[] = [];

  pk() {
    return "";
  }

  static urlRoot = "jobs";
}
