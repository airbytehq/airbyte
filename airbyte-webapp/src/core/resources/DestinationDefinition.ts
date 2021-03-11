import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface DestinationDefinition {
  destinationDefinitionId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
  documentationUrl: string;
}

export default class DestinationDefinitionResource
  extends BaseResource
  implements DestinationDefinition {
  readonly destinationDefinitionId: string = "";
  readonly name: string = "";
  readonly dockerRepository: string = "";
  readonly dockerImageTag: string = "";
  readonly documentationUrl: string = "";

  pk(): string {
    return this.destinationDefinitionId?.toString();
  }

  static urlRoot = "destination_definitions";

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<
    SchemaDetail<{ destinationDefinitions: DestinationDefinition[] }>
  > {
    return {
      ...super.listShape(),
      schema: { destinationDefinitions: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<DestinationDefinition>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }

  static updateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<DestinationDefinition>> {
    return {
      ...super.partialUpdateShape(),
      schema: this,
    };
  }
}
