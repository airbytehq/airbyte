import BaseResource from "./BaseResource";

export interface JobLogs {
  stdout: string[];
  stderr: string[];
}

export default class JobLogsResource extends BaseResource implements JobLogs {
  readonly stdout: string[] = [];
  readonly stderr: string[] = [];

  pk() {
    return "";
  }

  static urlRoot = "jobs";
}
