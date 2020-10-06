import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Source {
  sourceId: string;
  name: string;
  defaultDockerRepository?: string;
  defaultDockerImageVersion?: string;
}

export default class SourceResource extends BaseResource implements Source {
  readonly sourceId: string = "";
  readonly name: string = "";
  readonly defaultDockerRepository: string = "";
  readonly defaultDockerImageVersion: string = "";

  pk() {
    return this.sourceId?.toString();
  }

  static urlRoot = "sources";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { sources: [this.asSchema()] }
    };
  }

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this.asSchema()
    };
  }

  static updateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      schema: this.asSchema()
    };
  }

  static createShape<T extends typeof Resource>(this: T) {
    return {
      ...super.createShape(),
      schema: this.asSchema()
    };
  }
}
