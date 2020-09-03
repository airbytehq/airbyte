import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export type ScheduleProperties = {
  units: number;
  timeUnit: string;
};

type SourceInformation = {
  sourceId: string;
  sourceName: string;
  sourceImplementationId: string;
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
  syncSchema: any; // TODO: fix type
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
  readonly syncSchema: any | null = null; // TODO: fix it

  pk() {
    return this.connectionId?.toString();
  }

  static urlRoot = "connections";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { connections: [this.asSchema()] }
    };
  }

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
      schema: this.asSchema()
    };
  }

  static listWebShape<T extends typeof Resource>(this: T) {
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
}
