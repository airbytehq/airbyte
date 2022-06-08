export interface Logs {
  file?: Blob;
}

export enum LogType {
  Server = "server",
  Scheduler = "scheduler",
}
