import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export type ScheduleProperties = {
  units: number;
  timeUnit: string;
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
      schema: this.asSchema()
    };
  }

  static updateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      schema: this.asSchema()
    };
  }
}
