import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

type propertiesType = {
  [key: string]: any;
};

export type specification = {
  properties: propertiesType;
  required: string[];
};

export interface SourceSpecification {
  sourceSpecificationId: string;
  sourceId: string;
  documentation: string;
  connectionSpecification: specification;
}

export default class SourceSpecificationResource extends BaseResource
  implements SourceSpecification {
  readonly sourceSpecificationId: string = "";
  readonly sourceId: string = "";
  readonly documentation: string = "";
  readonly connectionSpecification: specification = {
    properties: {},
    required: []
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
