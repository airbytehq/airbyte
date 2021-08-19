import BaseResource from "./BaseResource";
import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";

export interface DbMigrationInfoItem {
  migrationType: string;
  migrationVersion: string;
  migrationDescription: string;
  migrationState?: string;
  migratedBy?: string;
  migratedAt?: bigint;
  migrationScript?: string;
}

export interface DbMigrationInfoResult {
  migrations: Array<DbMigrationInfoItem>;
}

export interface DbMigrationMigrateResult {
  initialVersion: string;
  targetVersion?: string;
  migrationsExecuted: number;
  migrations: Array<DbMigrationInfoItem>;
}

export default class DbMigrationResource
  extends BaseResource
  implements DbMigrationInfoItem {
  readonly migrationType: string = "";
  readonly migrationVersion: string = "";
  readonly migrationDescription: string = "";

  pk(): string {
    return "1";
  }

  static urlRoot = "db_migrations";

  static infoShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<DbMigrationInfoResult>> {
    return {
      ...super.detailShape(),
      getFetchKey: (params: { database: string }) =>
        `POST /info` + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<DbMigrationInfoResult> => {
        return await this.fetch("post", `${this.url(params)}/info`, params);
      },
      schema: this,
    };
  }

  static migrateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<DbMigrationMigrateResult>> {
    return {
      ...super.updateShape(),
      getFetchKey: (params) => `POST /migrate` + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, unknown>>
      ): Promise<DbMigrationMigrateResult> => {
        return await this.fetch("post", `${this.url(params)}/migrate`, params);
      },
      schema: this,
    };
  }
}
