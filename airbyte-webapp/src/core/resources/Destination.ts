import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Destination {
  destinationId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
}

export default class DestinationResource extends BaseResource
  implements Destination {
  readonly destinationId: string = "";
  readonly name: string = "";
  readonly dockerRepository: string = "";
  readonly dockerImageTag: string = "";
  readonly documentationUrl: string = "";

  pk() {
    return this.destinationId?.toString();
  }

  static urlRoot = "destinations";

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
}
