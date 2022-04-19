import { ReadShape, Resource, SchemaDetail } from "rest-hooks";

import BaseResource from "./BaseResource";
import { SourceDiscoverSchemaRead, SyncSchema } from "core/domain/catalog";
import { toInnerModel } from "core/domain/catalog/fieldUtil";
import { JobInfo } from "../domain/job/Job";

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
        const response = await this.fetch(
          "post",
          `${this.url(params)}/discover_schema`,
          params
        );

        const result = toInnerModel(response);

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
