import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export type propertiesType = {
  [key: string]: any;
};

export type specification = {
  properties: propertiesType;
  required: string[];
};

export interface SourceDefinitionSpecification {
  sourceDefinitionId: string;
  documentationUrl: string;
  connectionSpecification: specification;
}

export default class SourceDefinitionSpecificationResource extends BaseResource
  implements SourceDefinitionSpecification {
  readonly sourceDefinitionId: string = "";
  readonly documentationUrl: string = "";
  readonly connectionSpecification: specification = {
    properties: {},
    required: []
  };

  pk() {
    return this.sourceDefinitionId?.toString();
  }

  static urlRoot = "source_definition_specifications";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this
    };
  }
}
