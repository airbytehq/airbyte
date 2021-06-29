import { ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";
import { ConnectionSpecification } from "core/domain/connection";
import { DestinationSyncMode } from "../domain/catalog";

export interface DestinationDefinitionSpecification {
  destinationDefinitionId: string;
  connectionSpecification: ConnectionSpecification;
  documentationUrl: string;
  supportedDestinationSyncModes: DestinationSyncMode[];
  supportsDbt: boolean;
  supportsNormalization: boolean;
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
