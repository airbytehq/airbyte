import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface DestinationSpecification {
  destinationSpecificationId: string;
  destinationId: string;
  connectionSpecification: {
    properties: any;
    required: [string];
  };
  documentation: string;
}

export type specification = {
  properties: any;
  required: [string];
};

export interface DestinationSpecification {
  destinationSpecificationId: string;
  destinationId: string;
  connectionSpecification: specification;
}

export default class DestinationSpecificationResource extends BaseResource
  implements DestinationSpecification {
  readonly destinationSpecificationId: string = "";
  readonly destinationId: string = "";
  readonly documentation: string = "";
  readonly connectionSpecification: specification = {
    properties: {},
    required: [""]
  };

  pk() {
    return this.destinationSpecificationId?.toString();
  }

  static urlRoot = "destination_specifications";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this.asSchema()
    };
  }
}
