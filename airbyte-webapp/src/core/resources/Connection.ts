import { FetchOptions, Resource } from "rest-hooks";
import BaseResource, { NetworkError } from "./BaseResource";
import { SyncSchema } from "core/domain/catalog";

export type ScheduleProperties = {
  units: number;
  timeUnit: string;
};

type SourceInformation = {
  sourceDefinitionId: string;
  sourceName: string;
  sourceId: string;
  name: string;
  connectionConfiguration: any;
};

type DestinationInformation = {
  destinationDefinitionId: string;
  destinationName: string;
  destinationId: string;
  name: string;
  connectionConfiguration: any;
};

export interface Connection {
  connectionId: string;
  name: string;
  sourceId: string;
  destinationId: string;
  status: string;
  schedule: ScheduleProperties | null;
  syncCatalog: SyncSchema;
  source?: SourceInformation;
  destination?: DestinationInformation;
  lastSync?: number | null;
  isSyncing?: boolean;
}

export default class ConnectionResource extends BaseResource
  implements Connection {
  readonly connectionId: string = "";
  readonly name: string = "";
  readonly sourceId: string = "";
  readonly destinationId: string = "";
  readonly status: string = "";
  readonly message: string = "";
  readonly schedule: ScheduleProperties | null = null;
  readonly source: SourceInformation | undefined = undefined;
  readonly destination: DestinationInformation | undefined = undefined;
  readonly lastSync: number | undefined | null = null;
  readonly syncCatalog: SyncSchema = { streams: [] };
  readonly isSyncing: boolean = false;

  pk() {
    return this.connectionId?.toString();
  }

  static urlRoot = "connections";

  static getFetchOptions(): FetchOptions {
    return {
      pollFrequency: 2500 // every 2,5 seconds
    };
  }

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: {
        connectionId: string;
        withRefreshedCatalog?: boolean;
      }) => "POST /web_backend/get" + JSON.stringify(params),
      fetch: async (params: any): Promise<any> =>
        await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/get`,
          params
        ),
      schema: this
    };
  }

  static updateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: any
      ): Promise<any> => {
        const result = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/connections/update`,
          body
        );

        if (result.status === "failure") {
          const e = new NetworkError(result);
          e.status = result.status;
          e.message = result.message;
          throw e;
        }

        return result;
      },
      schema: this
    };
  }

  static createShape<T extends typeof Resource>(this: T) {
    return {
      ...super.createShape(),
      schema: this,
      fetch: async (
        params: Readonly<object>,
        body: Readonly<object>
      ): Promise<any> =>
        await this.fetch("post", `${this.url(params)}/create`, body).then(
          response => ({
            ...response,
            // will remove it if BE returns resource in /web_backend/get format
            ...params
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
      schema: { connections: [this] }
    };
  }

  static updateStoreAfterDeleteShape<T extends typeof Resource>(this: T) {
    return {
      ...super.deleteShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /app/delete" + JSON.stringify(params),
      fetch: async (): Promise<any> => {
        return null;
      }
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

  static reset<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/reset" + JSON.stringify(params),
      fetch: async (
        params: Readonly<{ connectionId: string }>
      ): Promise<any> => {
        await this.fetch("post", `${this.url(params)}/reset`, params);
        return {
          connectionId: params.connectionId
        };
      }
    };
  }

  static syncShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/sync" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        await this.fetch("post", `${this.url(params)}/sync`, params);
        return {
          connectionId: params.connectionId
        };
      }
    };
  }
}
