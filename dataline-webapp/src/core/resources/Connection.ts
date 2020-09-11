import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export type ScheduleProperties = {
  units: number;
  timeUnit: string;
};

export type SyncSchemaColumn = {
  name: string;
  selected: boolean;
  type: string;
};

export type SyncSchema = {
  tables: {
    name: string;
    columns: SyncSchemaColumn[];
  }[];
};

type SourceInformation = {
  sourceId: string;
  sourceName: string;
  sourceImplementationId: string;
  name: string;
  connectionConfiguration: any;
};

export interface Connection {
  connectionId: string;
  name: string;
  sourceImplementationId: string;
  destinationImplementationId: string;
  syncMode: string;
  status: string;
  schedule: ScheduleProperties | null;
  syncSchema: SyncSchema;
  source?: SourceInformation;
  lastSync?: number | null;
}

export default class ConnectionResource extends BaseResource
  implements Connection {
  readonly connectionId: string = "";
  readonly name: string = "";
  readonly sourceImplementationId: string = "";
  readonly destinationImplementationId: string = "";
  readonly syncMode: string = "";
  readonly status: string = "";
  readonly schedule: ScheduleProperties | null = null;
  readonly source: SourceInformation | undefined = undefined;
  readonly lastSync: number | undefined | null = null;
  readonly syncSchema: SyncSchema = { tables: [] };

  pk() {
    return this.connectionId?.toString();
  }

  static urlRoot = "connections";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /web_backend/get" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> =>
        await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/get`,
          params
        ),
      schema: this.asSchema()
    };
  }

  static updateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      schema: this.asSchema()
    };
  }

  static createShape<T extends typeof Resource>(this: T) {
    return {
      ...super.createShape(),
      schema: this.asSchema(),
      fetch: async (
        params: Readonly<Record<string, string | number>>,
        body: Readonly<object>
      ): Promise<any> =>
        await this.fetch("post", `${this.url(params)}/create`, body).then(
          response => ({
            ...response,
            // will remove it if BE returns resource in /web_backend/get format
            source: params
          })
        )
    };
  }

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      getFetchKey: (params: { workspaceId: string }) =>
        "POST /web_backend/list" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> =>
        await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/list`,
          params
        ),
      schema: { connections: [this.asSchema()] }
    };
  }

  static deleteShape<T extends typeof Resource>(this: T) {
    return {
      ...super.deleteShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /web_backend/delete" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => params
    };
  }

  static updateStateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /web_backend/update" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>,
        body: any
      ): Promise<any> => {
        return { ...params, ...body };
      }
    };
  }

  // TODO: fix error
  static syncShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/sync" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const result = await this.fetch(
          "post",
          `${this.url(params)}/sync`,
          params
        );
        return result;
      }
    };
  }
}
