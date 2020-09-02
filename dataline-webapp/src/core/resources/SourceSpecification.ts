import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface SourceSpecification {
  sourceSpecificationId: string;
  sourceId: string;
  connectionSpecification: {
    properties: any;
    required: [string];
  };
}

export type specification = {
  properties: any;
  required: [string];
};

export interface SourceSpecification {
  sourceSpecificationId: string;
  sourceId: string;
  connectionSpecification: specification;
}

export default class SourceSpecificationResource extends BaseResource
  implements SourceSpecification {
  readonly sourceSpecificationId: string = "";
  readonly sourceId: string = "";
  readonly connectionSpecification: specification = {
    properties: {},
    required: [""]
  };

  pk() {
    return this.sourceSpecificationId?.toString();
  }

  static urlRoot = "source_specifications";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this.asSchema()
    };
  }
}
