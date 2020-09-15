import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export type SyncSchemaColumn = {
  name: string;
  selected: boolean;
  type: string;
};

export type SyncSchema = {
  tables: {
    name: string;
    columns: SyncSchemaColumn[];
  }[];
};

export interface Schema {
  id: string;
  schema: SyncSchema;
}

export default class SchemaResource extends BaseResource implements Schema {
  readonly schema: SyncSchema = { tables: [] };
  readonly id: string = "";

  pk() {
    return this.id?.toString();
  }

  static urlRoot = "source_implementations";

  static schemaShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: { sourceImplementationId: string }) =>
        `POST /source_implementations/discover_schema` + JSON.stringify(params),
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
          id: params.sourceImplementationId
        };
      },
      schema: this.asSchema()
    };
  }
}
