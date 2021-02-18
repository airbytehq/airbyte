import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface DestinationDefinitionSpecification {
  destinationDefinitionId: string;
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

export default class DestinationDefinitionSpecificationResource
  extends BaseResource
  implements DestinationDefinitionSpecification {
  readonly destinationDefinitionId: string = "";
  readonly documentationUrl: string = "";
  readonly connectionSpecification: specification = {
    properties: {},
    required: [""]
  };

  pk() {
    return this.destinationDefinitionId?.toString();
  }

  static urlRoot = "destination_definition_specifications";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this
    };
  }
}
