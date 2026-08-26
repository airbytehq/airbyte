---
id: airbyte-mcp-registry
title: airbyte.mcp.registry
---

Airbyte connector registry MCP operations.

# registry module

MCP primitives registered by the `registry` module of the `airbyte-mcp` server: **4** tool(s), **0** prompt(s), **0** resource(s).

## Tools (4)

<a id="get_api_docs_urls"></a>

### get_api_docs_urls

**Hints:** `read-only` · `idempotent`

Get API documentation URLs for a connector.

This tool retrieves documentation URLs for a connector's upstream API from multiple sources:
- Registry metadata (documentationUrl, externalDocumentationUrls)
- Connector manifest.yaml file (data.externalDocumentationUrls)

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connector_name` | `string` | yes | — | The canonical connector name (e.g., 'source-facebook-marketing', 'destination-snowflake') |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connector_name": {
      "description": "The canonical connector name (e.g., 'source-facebook-marketing', 'destination-snowflake')",
      "type": "string"
    }
  },
  "required": [
    "connector_name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "anyOf": [
        {
          "items": {
            "description": "API documentation URL information.",
            "properties": {
              "title": {
                "type": "string"
              },
              "url": {
                "type": "string"
              },
              "source": {
                "type": "string"
              },
              "type": {
                "default": "other",
                "type": "string"
              },
              "requiresLogin": {
                "default": false,
                "type": "boolean"
              }
            },
            "required": [
              "title",
              "url",
              "source"
            ],
            "type": "object"
          },
          "type": "array"
        },
        {
          "const": "Connector not found.",
          "type": "string"
        }
      ]
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="get_connector_info"></a>

### get_connector_info

**Hints:** `read-only` · `idempotent`

Get metadata, documentation URL, config spec, and manifest URL for a connector.

`config_spec_jsonschema` is fetched from the public connector registry over
HTTP (no Docker or local install required), preferring the `cloud` spec and
falling back to `oss`. It is `None` when the registry has no spec available
for the connector.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connector_name` | `string` | yes | — | The name of the connector to get information for. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connector_name": {
      "description": "The name of the connector to get information for.",
      "type": "string"
    }
  },
  "required": [
    "connector_name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "anyOf": [
        {
          "description": "@private Class to hold connector information.",
          "properties": {
            "connector_name": {
              "type": "string"
            },
            "connector_metadata": {
              "anyOf": [
                {
                  "description": "Metadata for a connector.",
                  "properties": {
                    "name": {
                      "type": "string"
                    },
                    "display_name": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "connector_type": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "definition_id": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "docker_repository": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "latest_available_version": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ]
                    },
                    "pypi_package_name": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ]
                    },
                    "language": {
                      "anyOf": [
                        {
                          "description": "The language of a connector.",
                          "enum": [
                            "python",
                            "java",
                            "manifest-only"
                          ],
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ]
                    },
                    "install_types": {
                      "items": {
                        "description": "The type of installation for a connector.",
                        "enum": [
                          "yaml",
                          "python",
                          "docker",
                          "java",
                          "installable",
                          "any"
                        ],
                        "type": "string"
                      },
                      "type": "array",
                      "uniqueItems": true
                    },
                    "suggested_streams": {
                      "anyOf": [
                        {
                          "items": {
                            "type": "string"
                          },
                          "type": "array"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "support_level": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "release_stage": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "source_type": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "documentation_url": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "release_date": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    },
                    "github_issue_label": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ],
                      "default": null
                    }
                  },
                  "required": [
                    "name",
                    "latest_available_version",
                    "pypi_package_name",
                    "language",
                    "install_types"
                  ],
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            },
            "documentation_url": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            },
            "config_spec_jsonschema": {
              "anyOf": [
                {
                  "additionalProperties": true,
                  "type": "object"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            },
            "manifest_url": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ],
              "default": null
            }
          },
          "required": [
            "connector_name"
          ],
          "type": "object"
        },
        {
          "const": "Connector not found.",
          "type": "string"
        }
      ]
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="get_connector_version_history"></a>

### get_connector_version_history

**Hints:** `read-only` · `idempotent`

Get version history for a connector.

This tool retrieves the version history for a connector, including:
- Version number
- Release date (from changelog, with registry override for recent versions)
- DockerHub URL for the version
- Changelog URL
- PR URL and title (scraped from changelog)

For the most recent N versions (default 5), release dates are fetched from the
registry for accuracy. For older versions, changelog dates are used.

**Returns:**

List of version information, sorted by most recent first.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connector_name` | `string` | yes | — | The name of the connector (e.g., 'source-faker', 'destination-postgres') |
| `num_versions_to_validate` | `integer` | no | `5` | Number of most recent versions to validate with registry data for accurate release dates. Defaults to 5. |
| `limit` | `integer \| null \| null` | no | `null` |  |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connector_name": {
      "description": "The name of the connector (e.g., 'source-faker', 'destination-postgres')",
      "type": "string"
    },
    "num_versions_to_validate": {
      "default": 5,
      "description": "Number of most recent versions to validate with registry data for accurate release dates. Defaults to 5.",
      "type": "integer"
    },
    "limit": {
      "anyOf": [
        {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "DEPRECATED: Use num_versions_to_validate instead. Maximum number of versions to return (most recent first). If specified, only the first N versions will be returned."
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "required": [
    "connector_name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "anyOf": [
        {
          "items": {
            "description": "Information about a specific connector version.",
            "properties": {
              "version": {
                "type": "string"
              },
              "release_date": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "null"
                  }
                ],
                "default": null
              },
              "docker_image_url": {
                "type": "string"
              },
              "changelog_url": {
                "type": "string"
              },
              "pr_url": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "null"
                  }
                ],
                "default": null
              },
              "pr_title": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "null"
                  }
                ],
                "default": null
              },
              "parsing_errors": {
                "items": {
                  "type": "string"
                },
                "type": "array"
              }
            },
            "required": [
              "version",
              "docker_image_url",
              "changelog_url"
            ],
            "type": "object"
          },
          "type": "array"
        },
        {
          "enum": [
            "Connector not found.",
            "Failed to fetch changelog."
          ],
          "type": "string"
        }
      ]
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="list_connectors"></a>

### list_connectors

**Hints:** `read-only` · `idempotent`

List available Airbyte connectors with optional filtering.

**Returns:**

List of connector names.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `keyword_filter` | `string \| null` | no | `null` | Filter connectors by keyword. |
| `connector_type_filter` | `enum("source", "destination") \| null` | no | `null` | Filter connectors by type ('source' or 'destination'). |
| `install_types` | `enum("java", "python", "yaml", "docker") \| array<enum("java", "python", "yaml", "docker")> \| null` | no | `null` | Filter connectors by install type.                 These are not mutually exclusive:                 - "python": Connectors that can be installed as Python packages.                 - "yaml": Connectors that can be installed simply via YAML download.                     These connectors are the fastest to install and run, as they do not require any                     additional dependencies.                 - "java": Connectors that can only be installed via Java. Since PyAirbyte does not                     currently ship with a JVM, these connectors will be run via Docker instead.                     In environments where Docker is not available, these connectors may not be                     runnable.                 - "docker": Connectors that can be installed via Docker. Note that all connectors                     can be run in Docker, so this filter should generally return the same results as                     not specifying a filter.                 If no install types are specified, all connectors will be returned. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "keyword_filter": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Filter connectors by keyword."
    },
    "connector_type_filter": {
      "anyOf": [
        {
          "enum": [
            "source",
            "destination"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Filter connectors by type ('source' or 'destination')."
    },
    "install_types": {
      "anyOf": [
        {
          "enum": [
            "java",
            "python",
            "yaml",
            "docker"
          ],
          "type": "string"
        },
        {
          "items": {
            "enum": [
              "java",
              "python",
              "yaml",
              "docker"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "\n                Filter connectors by install type.\n                These are not mutually exclusive:\n                - \"python\": Connectors that can be installed as Python packages.\n                - \"yaml\": Connectors that can be installed simply via YAML download.\n                    These connectors are the fastest to install and run, as they do not require any\n                    additional dependencies.\n                - \"java\": Connectors that can only be installed via Java. Since PyAirbyte does not\n                    currently ship with a JVM, these connectors will be run via Docker instead.\n                    In environments where Docker is not available, these connectors may not be\n                    runnable.\n                - \"docker\": Connectors that can be installed via Docker. Note that all connectors\n                    can be run in Docker, so this filter should generally return the same results as\n                    not specifying a filter.\n                If no install types are specified, all connectors will be returned.\n                "
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "items": {
        "type": "string"
      },
      "type": "array"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>