import Status from "core/statuses";
import { SourceDefinition, DestinationDefinition } from "core/domain/connector";

export interface JobMeta {
  id: number | string;
  configType: string;
  configId: string;
  createdAt: number;
  startedAt: number;
  updatedAt: number;
  status: Status | null;
}

export interface Logs {
  logLines: string[];
}

export interface Attempt {
  id: number;
  status: string;
  createdAt: number;
  updatedAt: number;
  endedAt: number;
  bytesSynced: number;
  recordsSynced: number;
}

export interface AttemptInfo {
  attempt: Attempt;
  logs: Logs;
}

export interface JobInfo extends JobMeta {
  logs: Logs;
}

export interface JobDetails {
  job: JobMeta;
  attempts: AttemptInfo[];
}

export interface JobDebugInfoMeta {
  airbyteVersion: string;
  id: number | string;
  configType: string;
  configId: string;
  status: Status | null;
  sourceDefinition: SourceDefinition;
  destinationDefinition: DestinationDefinition;
}

export interface JobDebugInfoDetails {
  job: JobDebugInfoMeta;
  attempts: AttemptInfo[];
}

export interface JobListItem {
  job: JobMeta;
  attempts: Attempt[];
}
