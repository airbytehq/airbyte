import { ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";
import { ConnectionSpecification } from "core/domain/connection";
import { SourceDefinitionSpecification } from "core/domain/connector/types";

export default class SourceDefinitionSpecificationResource
  extends BaseResource
  implements SourceDefinitionSpecification {
  readonly sourceDefinitionId: string = "";
  readonly documentationUrl: string = "";
  readonly connectionSpecification: ConnectionSpecification = {
    properties: {},
    required: [],
  };

  pk(): string {
    return this.sourceDefinitionId?.toString();
  }

  static urlRoot = "source_definition_specifications";

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<SourceDefinitionSpecification>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }
}
