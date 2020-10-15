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
  sourceId: string;
  documentationUrl: string;
  connectionSpecification: specification;
}

export default class SourceSpecificationResource extends BaseResource
  implements SourceSpecification {
  readonly sourceId: string = "";
  readonly documentationUrl: string = "";
  readonly connectionSpecification: specification = {
    properties: {},
    required: []
  };

  pk() {
    return this.sourceId?.toString();
  }

  static urlRoot = "source_specifications";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this.asSchema()
    };
  }
}
