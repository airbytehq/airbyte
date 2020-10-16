import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface DestinationSpecification {
  destinationId: string;
  connectionSpecification: {
    properties: any;
    required: [string];
  };
  documentationUrl: string;
}

export type specification = {
  properties: any;
  required: [string];
};

export interface DestinationSpecification {
  destinationId: string;
  connectionSpecification: specification;
}

export default class DestinationSpecificationResource extends BaseResource
  implements DestinationSpecification {
  readonly destinationId: string = "";
  readonly documentationUrl: string = "";
  readonly connectionSpecification: specification = {
    properties: {},
    required: [""]
  };

  pk() {
    return this.destinationId?.toString();
  }

  static urlRoot = "destination_specifications";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this.asSchema()
    };
  }
}
