import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export type SyncSchemaField = {
  name: string;
  selected: boolean;
  type: string;
};

export type SyncSchema = {
  streams: {
    name: string;
    fields: SyncSchemaField[];
  }[];
};

export interface Schema {
  id: string;
  schema: SyncSchema;
}

export default class SchemaResource extends BaseResource implements Schema {
  readonly schema: SyncSchema = { streams: [] };
  readonly id: string = "";

  pk() {
    return this.id?.toString();
  }

  static urlRoot = "sources";

  static schemaShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: { sourceId: string }) =>
        `POST /sources/discover_schema` + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const result = await this.fetch(
          "post",
          `${this.url(params)}/discover_schema`,
          params
        );
        return {
          schema: result?.schema,
          id: params.sourceId
        };
      },
      schema: this.asSchema()
    };
  }
}
