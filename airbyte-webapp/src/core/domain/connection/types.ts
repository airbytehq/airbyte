// eslint-disable-next-line @typescript-eslint/no-explicit-any
import { SyncSchema } from "../catalog";
import { Source } from "../../resources/Source";
import { Destination } from "../../resources/Destination";
import { Operation } from "./operation";
import { ScheduleProperties } from "../../resources/Connection";

type ConnectionConfiguration = any;

type ConnectionSpecification = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  properties: any;
  required: string[];
};

export type { ConnectionConfiguration, ConnectionSpecification };

export enum ConnectionNamespaceDefinition {
  Source = "source",
  Destination = "destination",
  CustomFormat = "customformat",
}

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
