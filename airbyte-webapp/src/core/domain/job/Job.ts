import { SourceDefinition, DestinationDefinition } from "core/domain/connector";
import Status from "core/statuses";

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

enum FailureOrigin {
  SOURCE = "source",
  DESTINATION = "destination",
  REPLICATION = "replication",
  PERSISTENCE = "persistence",
  NORMALIZATION = "normalization",
  DBT = "dbt",
}

enum FailureType {
  CONFIG_ERROR = "config_error",
  SYSTEM_ERROR = "system_error",
  MANUAL_CANCELLATION = "manual_cancellation",
}

export interface Failure {
  failureOrigin?: FailureOrigin;
  failureType?: FailureType;
  externalMessage?: string;
  stacktrace?: string;
  retryable?: boolean;
  timestamp: number;
}

export interface FailedSummary {
  failures: Failure[];
  partialSuccess?: boolean;
}

export interface TotalStats {
  recordsEmitted: number;
  bytesEmitted: number;
  stateMessagesEmitted: number;
  recordsCommitted: number;
}

export interface Attempt {
  id: number;
  status: string;
  createdAt: number;
  updatedAt: number;
  endedAt: number;
  bytesSynced: number;
  recordsSynced: number;
  totalStats?: TotalStats;
  failureSummary?: FailedSummary;
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
  id: number;
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
