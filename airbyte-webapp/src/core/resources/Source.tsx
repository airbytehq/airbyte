import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";
import { ConnectionConfiguration } from "core/domain/connection";
import { Source } from "core/domain/connector";

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
        await this.fetch("post", `${super.rootUrl()}sources/create`, body),
    };
  }
}

export default SourceResource;
