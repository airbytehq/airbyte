import {
  FetchOptions,
  FetchShape,
  MutateShape,
  ReadShape,
  Resource,
  SchemaDetail,
} from "rest-hooks";

import { SyncSchema } from "core/domain/catalog";
import { CommonRequestError } from "core/request/CommonRequestError";
import { Source } from "./Source";
import { Destination } from "./Destination";

import BaseResource from "./BaseResource";
import {
  ConnectionNamespaceDefinition,
  Connection,
  ScheduleProperties,
  Operation,
} from "core/domain/connection";

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

  static getFetchOptions(): FetchOptions {
    return {
      pollFrequency: 2500, // every 2,5 seconds
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Connection>> {
    return {
      ...super.detailShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /web_backend/get" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, unknown>>
      ): Promise<Connection> =>
        await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/get`,
          params
        ),
      schema: this,
    };
  }

  static updateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Connection>> {
    return {
      ...super.partialUpdateShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: Record<string, unknown>
      ): Promise<Connection> => {
        const result = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/update`,
          body
        );

        if (result.status === "failure") {
          throw new CommonRequestError(result, result.message);
        }

        return result;
      },
      schema: this,
    };
  }

  static createShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Connection>> {
    return {
      ...super.createShape(),
      schema: this,
      fetch: async (
        _: Readonly<Record<string, string>>,
        body: Readonly<Record<string, unknown>>
      ): Promise<Connection> =>
        await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/create`,
          body
        ),
    };
  }

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<{ connections: Connection[] }>> {
    return {
      ...super.listShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<{ connections: Connection[] }> =>
        await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/list`,
          params
        ),
      schema: { connections: [this] },
    };
  }

  static updateStoreAfterDeleteShape<T extends typeof Resource>(
    this: T
  ): FetchShape<SchemaDetail<Connection>> {
    return {
      ...super.deleteShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /app/delete" + JSON.stringify(params),
      fetch: async (): Promise<null> => null,
    };
  }

  static updateStateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Connection>> {
    return {
      ...super.partialUpdateShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /web_backend/update" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>,
        body: Partial<Connection>
      ): Promise<Partial<Connection>> => {
        return { ...params, ...body };
      },
    };
  }

  static reset<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Connection>> {
    return {
      ...super.detailShape(),
      getFetchKey: (params: Readonly<Record<string, unknown>>) =>
        "POST " + this.url(params) + "/reset" + JSON.stringify(params),
      fetch: async (
        params: Readonly<{ connectionId: string }>
      ): Promise<{ connectionId: string }> => {
        await this.fetch("post", `${this.url(params)}/reset`, params);
        return {
          connectionId: params.connectionId,
        };
      },
    };
  }

  static syncShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Connection>> {
    return {
      ...super.detailShape(),
      getFetchKey: (params: Readonly<Record<string, unknown>>) =>
        "POST " + this.url(params) + "/sync" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string>>
      ): Promise<{ connectionId: string }> => {
        await this.fetch("post", `${this.url(params)}/sync`, params);
        return {
          connectionId: params.connectionId,
        };
      },
    };
  }
}
