import { ReadShape, Resource, SchemaDetail } from "rest-hooks";

import BaseResource from "./BaseResource";
import { SourceDiscoverSchemaRead, SyncSchema } from "core/domain/catalog";
import { JobInfo } from "core/domain/job";
import Status from "../statuses";
import { CommonRequestError } from "../request/CommonRequestError";

export interface Schema extends SourceDiscoverSchemaRead {
  id: string;
}

export default class SchemaResource extends BaseResource implements Schema {
  readonly catalog: SyncSchema = { streams: [] };
  readonly id: string = "";
  readonly jobInfo?: JobInfo = undefined;

  pk(): string {
    return this.id?.toString();
  }

  static urlRoot = "sources";

  static schemaShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Schema>> {
    return {
      ...super.detailShape(),
      fetch: async (params: { sourceId: string }): Promise<Schema> => {
        const result = await this.fetch(
          "post",
          `${this.url(params)}/discover_schema`,
          params
        );

        if (result.jobInfo?.status === Status.FAILED || !result.catalog) {
          // @ts-ignore address this case
          const e = new CommonRequestError(result);
          // Generate error with failed status and received logs
          e._status = 400;
          // @ts-ignore address this case
          e.response = result.jobInfo;
          throw e;
        }

        return {
          catalog: result.catalog,
          jobInfo: result.jobInfo,
          id: params.sourceId,
        };
      },
      schema: this,
    };
  }
}
