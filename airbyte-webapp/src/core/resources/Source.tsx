import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";
import { ConnectionConfiguration } from "core/domain/connection";

export interface Source {
  sourceId: string;
  name: string;
  sourceName: string;
  workspaceId: string;
  sourceDefinitionId: string;
  connectionConfiguration: ConnectionConfiguration;
}

export class SourceResource extends BaseResource implements Source {
  readonly sourceId: string = "";
  readonly name: string = "";
  readonly sourceName: string = "";
  readonly sourceDefinitionId: string = "";
  readonly workspaceId: string = "";
  readonly connectionConfiguration: ConnectionConfiguration = {};

  pk(): string {
    return this.sourceId?.toString();
  }

  static urlRoot = "sources";

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<{ sources: Source[] }>> {
    return {
      ...super.listShape(),
      schema: { sources: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Source>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }

  // TODO: fix detailShape here as it is actually createShape
  // eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
  static recreateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: Readonly<Partial<Source>>
      ): Promise<Source> => {
        const response = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/sources/recreate`,
          body
        );
        return response;
      },
      schema: this,
    };
  }

  static createShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Source>> {
    return {
      ...super.createShape(),
      schema: this,
      fetch: async (
        _: Readonly<Record<string, string>>,
        body: Readonly<Record<string, unknown>>
      ): Promise<Source> =>
        await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/sources/create`,
          body
        ),
    };
  }
}

export default SourceResource;
