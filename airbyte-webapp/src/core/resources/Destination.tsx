import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Destination {
  destinationId: string;
  name: string;
  destinationName: string;
  workspaceId: string;
  destinationDefinitionId: string;
  connectionConfiguration: any; // TODO: fix type
}

export default class DestinationResource extends BaseResource
  implements Destination {
  readonly destinationId: string = "";
  readonly name: string = "";
  readonly destinationName: string = "";
  readonly workspaceId: string = "";
  readonly destinationDefinitionId: string = "";
  readonly connectionConfiguration: any = [];

  pk() {
    return this.destinationId?.toString();
  }

  static urlRoot = "destinations";

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
        params: { destinationId: string },
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

  static checkConnectionShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: { connectionId: string }) =>
        "POST /v1/destinations/check_connection" + JSON.stringify(params),
      fetch: async (params: { destinationId: string }): Promise<any> => {
        const checkConnectionResult = await this.fetch(
          "post",
          `${this.url(params)}/check_connection`,
          params
        );

        return checkConnectionResult;
      },
      schema: { status: "", message: "" }
    };
  }

  static recreateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.updateShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: Readonly<object>
      ): Promise<any> => {
        const response = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/destinations/recreate`,
          body
        );
        return response;
      },
      schema: this.asSchema()
    };
  }
}
