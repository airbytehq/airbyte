import { SourceDefinitionSpecificationRead } from "core/request/AirbyteClient";

export const mockSourceDefinition: SourceDefinitionSpecificationRead = {
  sourceDefinitionId: "6371b14b-bc68-4236-bfbd-468e8df8e968",
  documentationUrl: "https://docs.airbyte.io/integrations/sources/pokeapi",
  connectionSpecification: {
    type: "object",
    title: "Pokeapi Spec",
    $schema: "http://json-schema.org/draft-07/schema#",
    required: ["pokemon_name"],
    properties: {
      pokemon_name: {
        type: "string",
        title: "Pokemon Name",
        pattern: "^[a-z0-9_\\-]+$",
        examples: ["ditto", "luxray", "snorlax"],
        description: "Pokemon requested from the API.",
      },
    },
    additionalProperties: false,
  },
  jobInfo: {
    id: "c00ebf34-2c2e-4d7a-9164-3a3eff32b933",
    configType: "get_spec",
    configId: "Optional.empty",
    createdAt: 1669740832547,
    endedAt: 1669740832547,
    succeeded: true,
    logs: { logLines: [] },
  },
};
