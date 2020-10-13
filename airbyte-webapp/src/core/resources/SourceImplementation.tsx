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
      fetch: async (
        params: { sourceImplementationId: string },
        body: any
      ): Promise<any> => {
        const sourceResult = await this.fetch(
          "post",
          `${this.url(params)}/update`,
          body
        );

        const checkConnectionResult = await this.fetch(
          "post",
          `${this.url(params)}/check_connection`,
          params
        );

        return {
          source: sourceResult,
          ...checkConnectionResult
        };
      },
      schema: { source: this.asSchema(), status: "", message: "" }
    };
  }

  static createShape<T extends typeof Resource>(this: T) {
    return {
      ...super.createShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: Readonly<object>
      ): Promise<any> => {
        const response = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/source_implementations/create`,
          body
        );
        return response;
      },
      schema: this.asSchema()
    };
  }

  static recreateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: Readonly<any>
      ): Promise<object> => {
        const response = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/source_implementations/recreate`,
          body
        );
        return response;
      },
      schema: this.asSchema()
    };
  }
}
