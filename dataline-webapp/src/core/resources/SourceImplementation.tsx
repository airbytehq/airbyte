import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface SourceImplementation {
  sourceImplementationId: string;
  name: string;
  workspaceId: string;
  sourceSpecificationId: string;
  sourceId: string;
  connectionConfiguration: any; // TODO: fix type
}

export default class SourceImplementationResource extends BaseResource
  implements SourceImplementation {
  readonly sourceImplementationId: string = "";
  readonly name: string = "";
  readonly sourceId: string = "";
  readonly workspaceId: string = "";
  readonly sourceSpecificationId: string = "";
  readonly connectionConfiguration: any = [];

  pk() {
    return this.sourceImplementationId?.toString();
  }

  static urlRoot = "source_implementations";

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
