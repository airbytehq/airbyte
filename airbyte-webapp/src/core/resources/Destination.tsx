import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";

import { ConnectionConfiguration } from "core/domain/connection";
import BaseResource from "./BaseResource";
import { Destination } from "core/domain/connector";

export class DestinationResource extends BaseResource implements Destination {
  readonly destinationId: string = "";
  readonly name: string = "";
  readonly destinationName: string = "";
  readonly workspaceId: string = "";
  readonly destinationDefinitionId: string = "";
  readonly connectionConfiguration: ConnectionConfiguration = {};

  pk(): string {
    return this.destinationId?.toString();
  }

  static urlRoot = "destinations";

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<{ destinations: Destination[] }>> {
    return {
      ...super.listShape(),
      schema: { destinations: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Destination>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }

  // TODO: remove?
  static recreateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Destination>> {
    return {
      ...super.updateShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        body: Record<string, unknown>
      ): Promise<Destination> => {
        const response = await this.fetch(
          "post",
          `${super.rootUrl()}web_backend/destinations/recreate`,
          body
        );
        return response;
      },
      schema: this,
    };
  }

  static createShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Destination>> {
    return {
      ...super.createShape(),
      schema: this,
      fetch: async (
        _: Readonly<Record<string, string>>,
        body: Readonly<Record<string, unknown>>
      ): Promise<Destination> =>
        await this.fetch("post", `${super.rootUrl()}destinations/create`, body),
    };
  }
}

export default DestinationResource;
