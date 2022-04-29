import { SyncSchema } from "core/domain/catalog";
import { AirbyteJSONSchema } from "core/jsonSchema";
import Status from "core/statuses";

import { Destination, Source } from "../connector";
import { Operation } from "./operation";

type ConnectionConfiguration = unknown;

type ConnectionSpecification = AirbyteJSONSchema;

export type { ConnectionConfiguration, ConnectionSpecification };

export enum ConnectionNamespaceDefinition {
  Source = "source",
  Destination = "destination",
  CustomFormat = "customformat",
}

export enum ConnectionSchedule {
  Minutes = "minutes",
  Hours = "hours",
  Days = "days",
  Weeks = "weeks",
  Months = "months",
}

export type ScheduleProperties = {
  units: number;
  timeUnit: ConnectionSchedule;
};

export enum ConnectionStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  DEPRECATED = "depreacted",
}

export interface Connection {
  connectionId: string;
  name: string;
  prefix: string;
  sourceId: string;
  destinationId: string;
  status: ConnectionStatus;
  schedule: ScheduleProperties | null;
  syncCatalog: SyncSchema;
  latestSyncJobCreatedAt?: number | null;
  namespaceDefinition: ConnectionNamespaceDefinition;
  namespaceFormat: string;
  isSyncing?: boolean;
  latestSyncJobStatus: Status | null;
  operationIds: string[];

  // WebBackend connection specific fields
  source: Source;
  destination: Destination;
  operations: Operation[];
  catalogId: string;
}
