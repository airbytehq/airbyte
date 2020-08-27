import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface SourceSpecification {
  sourceSpecificationId: string;
  sourceId: string;
  connectionSpecification: any; // TODO: fix type
}

export default class SourceSpecificationResource extends BaseResource
  implements SourceSpecification {
  readonly sourceSpecificationId: string = "";
  readonly sourceId: string = "";
  readonly connectionSpecification: any = null; // TODO: fix it

  pk() {
    return this.sourceSpecificationId?.toString();
  }

  static urlRoot = "source_specifications";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this.asSchema()
    };
  }
}
