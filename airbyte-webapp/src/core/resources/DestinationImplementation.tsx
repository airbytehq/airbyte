import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface DestinationImplementation {
  destinationImplementationId: string;
  name: string;
  workspaceId: string;
  destinationId: string;
  connectionConfiguration: any; // TODO: fix type
}

export default class DestinationImplementationResource extends BaseResource
  implements DestinationImplementation {
  readonly destinationImplementationId: string = "";
  readonly name: string = "";
  readonly workspaceId: string = "";
  readonly destinationId: string = "";
  readonly connectionConfiguration: any = [];

  pk() {
    return this.destinationImplementationId?.toString();
  }

  static urlRoot = "destination_implementations";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { destinations: [this.asSchema()] }
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
        params: { destinationImplementationId: string },
        body: any
      ): Promise<any> => {
        const destinationResult = await this.fetch(
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
          destination: destinationResult,
          ...checkConnectionResult
        };
      },
      schema: { destination: this.asSchema(), status: "", message: "" }
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
          `${super.rootUrl()}web_backend/destination_implementations/create`,
          body
        );
        return response;
      },
      schema: this.asSchema()
    };
  }
}
