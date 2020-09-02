import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface DestinationImplementation {
  destinationImplementationId: string;
  workspaceId: string;
  destinationSpecificationId: string;
  destinationId: string;
  connectionConfiguration: any; // TODO: fix type
}

export default class DestinationImplementationResource extends BaseResource
  implements DestinationImplementation {
  readonly destinationImplementationId: string = "";
  readonly workspaceId: string = "";
  readonly destinationId: string = "";
  readonly destinationSpecificationId: string = "";
  readonly connectionConfiguration: any = [];

  pk() {
    return this.destinationImplementationId?.toString();
  }

  static urlRoot = "destination_implementations";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { destinations: [this.asSchema()] }
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

  static createShape<T extends typeof Resource>(this: T) {
    return {
      ...super.createShape(),
      schema: this.asSchema()
    };
  }
}
