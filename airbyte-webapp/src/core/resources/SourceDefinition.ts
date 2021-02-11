import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface SourceDefinition {
  sourceDefinitionId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
  documentationUrl: string;
}

export default class SourceDefinitionResource extends BaseResource
  implements SourceDefinition {
  readonly sourceDefinitionId: string = "";
  readonly name: string = "";
  readonly dockerRepository: string = "";
  readonly dockerImageTag: string = "";
  readonly documentationUrl: string = "";

  pk() {
    return this.sourceDefinitionId?.toString();
  }

  static urlRoot = "source_definitions";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { sourceDefinitions: [this] }
    };
  }
}
