import { ReadShape, Resource, SchemaDetail } from "rest-hooks";

import { ConnectionSpecification } from "core/domain/connection";
import { DestinationSyncMode } from "core/domain/catalog";
import { DestinationDefinitionSpecification } from "core/domain/connector/types";

import BaseResource from "./BaseResource";

export default class DestinationDefinitionSpecificationResource
  extends BaseResource
  implements DestinationDefinitionSpecification {
  readonly destinationDefinitionId: string = "";
  readonly documentationUrl: string = "";
  readonly connectionSpecification: ConnectionSpecification = {
    properties: {},
    required: [""],
  };
  readonly supportedDestinationSyncModes: DestinationSyncMode[] = [];
  readonly supportsDbt: boolean = false;
  readonly supportsNormalization: boolean = false;

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
