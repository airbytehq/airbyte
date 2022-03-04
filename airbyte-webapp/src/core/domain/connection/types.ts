import { SyncSchema } from "core/domain/catalog";
import { Operation } from "./operation";
import { AirbyteJSONSchema } from "core/jsonSchema";
import { Destination, Source } from "../connector";

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

export interface Connection {
  connectionId: string;
  name: string;
  prefix: string;
  sourceId: string;
  destinationId: string;
  status: string;
  schedule: ScheduleProperties | null;
  syncCatalog: SyncSchema;
  latestSyncJobCreatedAt?: number | null;
  namespaceDefinition: ConnectionNamespaceDefinition;
  namespaceFormat: string;
  isSyncing?: boolean;
  latestSyncJobStatus: string | null;
  operationIds: string[];

  // WebBackend connection specific fields
  source: Source;
  destination: Destination;
  operations: Operation[];
}
