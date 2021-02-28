import { ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";
import { ConnectionSpecification } from "core/domain/connection";

export interface DestinationDefinitionSpecification {
  destinationDefinitionId: string;
  connectionSpecification: ConnectionSpecification;
  documentationUrl: string;
}

export default class DestinationDefinitionSpecificationResource
  extends BaseResource
  implements DestinationDefinitionSpecification {
  readonly destinationDefinitionId: string = "";
  readonly documentationUrl: string = "";
  readonly connectionSpecification: ConnectionSpecification = {
    properties: {},
    required: [""],
  };

  pk(): string {
    return this.destinationDefinitionId?.toString();
  }

  static urlRoot = "destination_definition_specifications";

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<DestinationDefinitionSpecification>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }
}
