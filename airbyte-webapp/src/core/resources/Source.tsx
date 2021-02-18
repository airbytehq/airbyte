import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Source {
  sourceId: string;
  name: string;
  sourceName: string;
  workspaceId: string;
  sourceDefinitionId: string;
  connectionConfiguration: any; // TODO: fix type
}

export default class SourceResource extends BaseResource implements Source {
  readonly sourceId: string = "";
  readonly name: string = "";
  readonly sourceName: string = "";
  readonly sourceDefinitionId: string = "";
  readonly workspaceId: string = "";
  readonly connectionConfiguration: any = [];

  pk() {
    return this.sourceId?.toString();
  }

  static urlRoot = "sources";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { sources: [this] }
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
      ...super.detailShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: Readonly<any>
      ): Promise<object> => {
        const response = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/sources/recreate`,
          body
        );
        return response;
      },
      schema: this
    };
  }
}
