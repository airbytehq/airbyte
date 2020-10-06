import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Destination {
  destinationId: string;
  name: string;
  defaultDockerRepository?: string;
  defaultDockerImageVersion?: string;
}

export default class DestinationResource extends BaseResource
  implements Destination {
  readonly destinationId: string = "";
  readonly name: string = "";
  readonly defaultDockerRepository: string = "";
  readonly defaultDockerImageVersion: string = "";

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
}
