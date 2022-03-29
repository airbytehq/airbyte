import { FetchShape, Resource, SchemaDetail } from "rest-hooks";

import { SyncSchema } from "core/domain/catalog";

import BaseResource from "./BaseResource";
import {
  Connection,
  ConnectionNamespaceDefinition,
  Operation,
  ScheduleProperties,
} from "core/domain/connection";
import { Destination, Source } from "core/domain/connector";

export type { Connection, ScheduleProperties };

export default class ConnectionResource
  extends BaseResource
  implements Connection {
  readonly connectionId: string = "";
  readonly name: string = "";
  readonly prefix: string = "";
  readonly sourceId: string = "";
  readonly destinationId: string = "";
  readonly status: string = "";
  readonly message: string = "";
  readonly namespaceFormat: string = "";
  readonly namespaceDefinition: ConnectionNamespaceDefinition =
    ConnectionNamespaceDefinition.Source;
  readonly schedule: ScheduleProperties | null = null;
  readonly operations: Operation[] = [];
  readonly source: Source = {} as Source;
  readonly destination: Destination = {} as Destination;
  readonly latestSyncJobCreatedAt: number | undefined | null = null;
  readonly latestSyncJobStatus: string | null = null;
  readonly syncCatalog: SyncSchema = { streams: [] };
  readonly isSyncing: boolean = false;
  readonly operationIds: string[] = [];

  pk(): string {
    return this.connectionId?.toString();
  }

  static urlRoot = "connections";

  static updateStoreAfterDeleteShape<T extends typeof Resource>(
    this: T
  ): FetchShape<SchemaDetail<Connection>> {
    return {
      ...super.deleteShape(),
      fetch: async (): Promise<null> => null,
    };
  }
}
