import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";

import { getService } from "core/servicesProvider";

import BaseResource from "./BaseResource";
import { DestinationDefinitionService } from "core/domain/connector/DestinationDefinitionService";

export interface DestinationDefinition {
  destinationDefinitionId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
  latestDockerImageTag: string;
  documentationUrl: string;
  icon: string;
}

export default class DestinationDefinitionResource
  extends BaseResource
  implements DestinationDefinition {
  readonly destinationDefinitionId: string = "";
  readonly name: string = "";
  readonly dockerRepository: string = "";
  readonly dockerImageTag: string = "";
  readonly latestDockerImageTag: string = "";
  readonly documentationUrl: string = "";
  readonly icon: string = "";

  pk(): string {
    return this.destinationDefinitionId?.toString();
  }

  static urlRoot = "destination_definitions";

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<
    SchemaDetail<{ destinationDefinitions: DestinationDefinition[] }>
  > {
    return {
      ...super.listShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<{ destinationDefinitions: DestinationDefinition[] }> => {
        const definition = await this.fetch(
          "post",
          `${this.url(params)}/list`,
          params
        );
        const latestDefinition = await this.fetch(
          "post",
          `${this.url(params)}/list_latest`,
          params
        );

        const result: DestinationDefinition[] = definition.destinationDefinitions.map(
          (destination: DestinationDefinition) => {
            const withLatest = latestDefinition.destinationDefinitions.find(
              (latestDestination: DestinationDefinition) =>
                latestDestination.destinationDefinitionId ===
                destination.destinationDefinitionId
            );

            return {
              ...destination,
              latestDockerImageTag: withLatest?.dockerImageTag,
            };
          }
        );

        return { destinationDefinitions: result };
      },
      schema: { destinationDefinitions: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<DestinationDefinition>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }

  static updateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<DestinationDefinition>> {
    return {
      ...super.partialUpdateShape(),
      fetch(
        _: Readonly<Record<string, unknown>>,
        body: DestinationDefinition
      ): Promise<DestinationDefinition> {
        return getService<DestinationDefinitionService>(
          "DestinationDefinitionService"
        ).update(body);
      },
      schema: this,
    };
  }
}
