import { SynchronousJobRead } from "../../request/AirbyteClient";

export interface Logs {
  logLines: string[];
}

export interface JobInfo extends SynchronousJobRead {
  logs: Logs;
}
