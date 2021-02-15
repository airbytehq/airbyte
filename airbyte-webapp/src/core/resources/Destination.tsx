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
      schema: { destinations: [this] }
    };
  }

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this
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
      schema: this
    };
  }
}
