import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface DestinationDefinition {
  destinationDefinitionId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
}

export default class DestinationDefinitionResource extends BaseResource
  implements DestinationDefinition {
  readonly destinationDefinitionId: string = "";
  readonly name: string = "";
  readonly dockerRepository: string = "";
  readonly dockerImageTag: string = "";
  readonly documentationUrl: string = "";

  pk() {
    return this.destinationDefinitionId?.toString();
  }

  static urlRoot = "destination_definitions";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { destinationDefinitions: [this] }
    };
  }

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this
    };
  }

  static updateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      schema: this
    };
  }
}
