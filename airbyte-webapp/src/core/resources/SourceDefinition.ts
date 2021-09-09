import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";
import { getService } from "core/servicesProvider";
import { SourceDefinitionService } from "../domain/connector/SourceDefinitionService";

export interface SourceDefinition {
  sourceDefinitionId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
  latestDockerImageTag: string;
  documentationUrl: string;
  icon: string;
}

export default class SourceDefinitionResource
  extends BaseResource
  implements SourceDefinition {
  readonly sourceDefinitionId: string = "";
  readonly name: string = "";
  readonly dockerRepository: string = "";
  readonly dockerImageTag: string = "";
  readonly latestDockerImageTag: string = "";
  readonly documentationUrl: string = "";
  readonly icon: string = "";

  pk(): string {
    return this.sourceDefinitionId?.toString();
  }

  static urlRoot = "source_definitions";

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<{ sourceDefinitions: SourceDefinition[] }>> {
    return {
      ...super.listShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<{ sourceDefinitions: SourceDefinition[] }> => {
        const [definition, latestDefinition] = await Promise.all([
          this.fetch("post", `${this.url(params)}/list`, params),
          this.fetch("post", `${this.url(params)}/list_latest`, params),
        ]);

        const result: SourceDefinition[] = definition.sourceDefinitions.map(
          (source: SourceDefinition) => {
            const withLatest = latestDefinition.sourceDefinitions.find(
              (latestSource: SourceDefinition) =>
                latestSource.sourceDefinitionId === source.sourceDefinitionId
            );

            return {
              ...source,
              latestDockerImageTag: withLatest?.dockerImageTag,
            };
          }
        );

        return { sourceDefinitions: result };
      },
      schema: { sourceDefinitions: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<SourceDefinition>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }

  static updateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<SourceDefinition>> {
    return {
      ...super.partialUpdateShape(),
      fetch(
        _: Readonly<Record<string, unknown>>,
        body: SourceDefinition
      ): Promise<SourceDefinition> {
        return getService<SourceDefinitionService>(
          "SourceDefinitionService"
        ).update(body);
      },
      schema: this,
    };
  }

  static createShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<SourceDefinition>> {
    return {
      ...super.createShape(),
      schema: this,
    };
  }
}
