/* eslint-disable no-template-curly-in-string */
import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { ConnectorIds } from "utils/connectors";

export const mockConnection: WebBackendConnectionRead = {
  connectionId: "a9c8e4b5-349d-4a17-bdff-5ad2f6fbd611",
  name: "Scrafty <> Heroku Postgres",
  namespaceDefinition: "source",
  namespaceFormat: "${SOURCE_NAMESPACE}",
  prefix: "",
  sourceId: "a3295ed7-4acf-4c0b-b16b-07a00e624a52",
  destinationId: "083a53bc-8bc2-4dc0-b05a-4273a96f3b93",
  geography: "auto",
  syncCatalog: {
    streams: [
      {
        stream: {
          name: "pokemon",
          jsonSchema: {
            type: "object",
            $schema: "http://json-schema.org/draft-07/schema#",
            properties: {
              id: {
                type: ["null", "integer"],
              },
              name: {
                type: ["null", "string"],
              },
              forms: {
                type: ["null", "array"],
                items: {
                  type: ["null", "object"],
                  properties: {
                    url: {
                      type: ["null", "string"],
                    },
                    name: {
                      type: ["null", "string"],
                    },
                  },
                },
              },
              moves: {
                type: ["null", "array"],
                items: {
                  type: ["null", "object"],
                  properties: {
                    move: {
                      type: ["null", "object"],
                      properties: {
                        url: {
                          type: ["null", "string"],
                        },
                        name: {
                          type: ["null", "string"],
                        },
                      },
                    },
                    version_group_details: {
                      type: ["null", "array"],
                      items: {
                        type: ["null", "object"],
                        properties: {
                          version_group: {
                            type: ["null", "object"],
                            properties: {
                              url: {
                                type: ["null", "string"],
                              },
                              name: {
                                type: ["null", "string"],
                              },
                            },
                          },
                          level_learned_at: {
                            type: ["null", "integer"],
                          },
                          move_learn_method: {
                            type: ["null", "object"],
                            properties: {
                              url: {
                                type: ["null", "string"],
                              },
                              name: {
                                type: ["null", "string"],
                              },
                            },
                          },
                        },
                      },
                    },
                  },
                },
              },
              order: {
                type: ["null", "integer"],
              },
              stats: {
                type: ["null", "array"],
                items: {
                  type: ["null", "object"],
                  properties: {
                    stat: {
                      type: ["null", "object"],
                      properties: {
                        url: {
                          type: ["null", "string"],
                        },
                        name: {
                          type: ["null", "string"],
                        },
                      },
                    },
                    effort: {
                      type: ["null", "integer"],
                    },
                    base_stat: {
                      type: ["null", "integer"],
                    },
                  },
                },
              },
              types: {
                type: ["null", "array"],
                items: {
                  type: ["null", "object"],
                  properties: {
                    slot: {
                      type: ["null", "integer"],
                    },
                    type: {
                      type: ["null", "object"],
                      properties: {
                        url: {
                          type: ["null", "string"],
                        },
                        name: {
                          type: ["null", "string"],
                        },
                      },
                    },
                  },
                },
              },
              height: {
                type: ["null", "integer"],
              },
              weight: {
                type: ["null", "integer"],
              },
              species: {
                type: ["null", "object"],
                properties: {
                  url: {
                    type: ["null", "string"],
                  },
                  name: {
                    type: ["null", "string"],
                  },
                },
              },
              sprites: {
                type: ["null", "object"],
                properties: {
                  back_shiny: {
                    type: ["null", "string"],
                  },
                  back_female: {
                    type: ["null", "string"],
                  },
                  front_shiny: {
                    type: ["null", "string"],
                  },
                  back_default: {
                    type: ["null", "string"],
                  },
                  front_female: {
                    type: ["null", "string"],
                  },
                  front_default: {
                    type: ["null", "string"],
                  },
                  back_shiny_female: {
                    type: ["null", "string"],
                  },
                  front_shiny_female: {
                    type: ["null", "string"],
                  },
                },
              },
              abilities: {
                type: ["null", "array"],
                items: {
                  type: ["null", "object"],
                  properties: {
                    slot: {
                      type: ["null", "integer"],
                    },
                    ability: {
                      type: ["null", "object"],
                      properties: {
                        url: {
                          type: ["null", "string"],
                        },
                        name: {
                          type: ["null", "string"],
                        },
                      },
                    },
                    is_hidden: {
                      type: ["null", "boolean"],
                    },
                  },
                },
              },
              held_items: {
                type: ["null", "array"],
                items: {
                  type: ["null", "object"],
                  properties: {
                    item: {
                      type: ["null", "object"],
                      properties: {
                        url: {
                          type: ["null", "string"],
                        },
                        name: {
                          type: ["null", "string"],
                        },
                      },
                    },
                    version_details: {
                      type: ["null", "array"],
                      items: {
                        type: ["null", "object"],
                        properties: {
                          rarity: {
                            type: ["null", "integer"],
                          },
                          version: {
                            type: ["null", "object"],
                            properties: {
                              url: {
                                type: ["null", "string"],
                              },
                              name: {
                                type: ["null", "string"],
                              },
                            },
                          },
                        },
                      },
                    },
                  },
                },
              },
              "is_default ": {
                type: ["null", "boolean"],
              },
              game_indices: {
                type: ["null", "array"],
                items: {
                  type: ["null", "object"],
                  properties: {
                    version: {
                      type: ["null", "object"],
                      properties: {
                        url: {
                          type: ["null", "string"],
                        },
                        name: {
                          type: ["null", "string"],
                        },
                      },
                    },
                    game_index: {
                      type: ["null", "integer"],
                    },
                  },
                },
              },
              base_experience: {
                type: ["null", "integer"],
              },
              location_area_encounters: {
                type: ["null", "string"],
              },
            },
          },
          supportedSyncModes: ["full_refresh"],
          defaultCursorField: [],
          sourceDefinedPrimaryKey: [],
        },
        config: {
          syncMode: "full_refresh",
          cursorField: [],
          destinationSyncMode: "append",
          primaryKey: [],
          aliasName: "pokemon",
          selected: true,
        },
      },
    ],
  },
  scheduleType: "manual",
  status: "active",
  operationIds: ["8af8ef4d-01b1-49c8-b145-23775f34a74b"],
  source: {
    sourceDefinitionId: ConnectorIds.Sources.PokeApi,
    sourceId: "a3295ed7-4acf-4c0b-b16b-07a00e624a52",
    workspaceId: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
    connectionConfiguration: {
      pokemon_name: "scrafty",
    },
    name: "Scrafty",
    sourceName: "PokeAPI",
  },
  destination: {
    destinationDefinitionId: ConnectorIds.Destinations.Postgres,
    destinationId: "083a53bc-8bc2-4dc0-b05a-4273a96f3b93",
    workspaceId: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
    connectionConfiguration: {
      ssl: false,
      host: "asdf",
      port: 5432,
      schema: "public",
      database: "asdf",
      password: "**********",
      username: "asdf",
      tunnel_method: {
        tunnel_method: "NO_TUNNEL",
      },
    },
    name: "Heroku Postgres",
    destinationName: "Postgres",
  },
  operations: [
    {
      workspaceId: "47c74b9b-9b89-4af1-8331-4865af6c4e4d",
      operationId: "8af8ef4d-01b1-49c8-b145-23775f34a74b",
      name: "Normalization",
      operatorConfiguration: {
        operatorType: "normalization",
        normalization: {
          option: "basic",
        },
      },
    },
  ],
  latestSyncJobCreatedAt: 1660227512,
  latestSyncJobStatus: "succeeded",
  isSyncing: false,
  catalogId: "bf31d1df-d7ba-4bae-b1ec-dac617b4f70c",
  schemaChange: "no_change",
  notifySchemaChanges: true,
  nonBreakingChangesPreference: "ignore",
};
