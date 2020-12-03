import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export type SyncSchemaField = {
  name: string;
  cleanedName: string;
  selected: boolean;
  type: string;
  dataType: string;
};

export type SyncSchemaStream = {
  name: string;
  cleanedName: string;
  fields: SyncSchemaField[];
  supportedSyncModes: string[];
  sourceDefinedCursor: boolean | null;
  defaultCursorField: string[];
  selected: boolean | null;
  syncMode: string | null;
  cursorField: string[];
};

export type SyncSchema = {
  streams: SyncSchemaStream[];
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
