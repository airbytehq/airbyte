import { Resource } from "rest-hooks";
import BaseResource, { NetworkError } from "./BaseResource";
import { JobInfo } from "./Scheduler";

export enum SyncMode {
  Incremental = "incremental",
  FullRefresh = "full_refresh"
}

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
  supportedSyncModes: SyncMode[];
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
  job_info?: JobInfo;
}

export default class SchemaResource extends BaseResource implements Schema {
  readonly schema: SyncSchema = { streams: [] };
  readonly id: string = "";
  readonly job_info: JobInfo | undefined = undefined;

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

        if (result.job_info.job.status === "failed" || !result.schema) {
          const e = new NetworkError(result);
          // Generate error with failed status and received logs
          e.status = 400;
          e.response = result.job_info;
          throw e;
        }

        return {
          schema: result.schema,
          job_info: result.job_info,
          id: params.sourceId
        };
      },
      schema: this.asSchema()
    };
  }
}
