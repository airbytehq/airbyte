---

products: embedded

---

# Source Templates

A source template controls which connectors appear in the Embedded widget and how their config screens look. When a customer opens the widget, only the sources backed by a template are selectable, so you can pre-set sensible defaults or restrict advanced settings.

The Airbyte platform comes with ready-to-use templates. You can also create templates specific to your organization if you need access to more integrations or if you want different default values.

## Creating source templates

Here is an example request to create a new template using only default values:

```bash
curl https://api.airbyte.ai/api/v1/integrations/templates/sources \

  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  --data-raw '{

    "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
    "actor_definition_id": "45b7d7e6-d7d5-4f31-8c1a-9fd96ce6ee35",
    "partial_default_config": {}
  }'

```

You can find the actor definition ID from the [Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

The `partial_default_config` is a JSON object representing keys from the connector spec for which you want to set default values so your users don't need to set them up themselves.

### Optional: add tags during creation

You can also add tags to organize and filter templates:

```bash
curl https://api.airbyte.ai/api/v1/integrations/templates/sources \

  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  --data-raw '{

    "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
    "actor_definition_id": "45b7d7e6-d7d5-4f31-8c1a-9fd96ce6ee35",
    "partial_default_config": {},
    "tags": ["crm", "pro-tier"]
  }'

```

See [Template Tags](./tags.md) for more information on organizing templates with tags.

## Updating source templates

You can update an existing source template using the PATCH endpoint:

```bash
curl -X PATCH https://api.airbyte.ai/api/v1/integrations/templates/sources/{id} \

  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  --data-raw '{

    "partial_default_config": {
      "api_key": "new_default_value"
    }
  }'

```

When a source template is updated, all existing sources created from it will also be updated.

## Listing templates

The [List Source Templates endpoint](https://api.airbyte.ai/api/v1/docs#tag/Template-Sources/operation/list_integrations_templates_sources) lists both the templates you created, as well as standard templates that are available to everyone using the platform.

### Filter by tags

You can filter source templates by tags:

```bash
curl 'https://api.airbyte.ai/api/v1/integrations/templates/sources?tags=crm&tags=sales&tags_mode=any' \

  -H 'Authorization: Bearer <token>'

```

**Tag Selection Modes:**

- `any` - Template must have at least one of the specified tags
- `all` - Template must have all of the specified tags

## Deleting templates

You can delete source templates by submitting a DELETE request to the API:

```bash
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}' \

  -H 'Authorization: Bearer <token>'

```

Sources created from a deleted source template will stop showing up in the widget.

## Managing template tags

### Add tag to source template

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}/tags \

  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "tag": "pro-tier"
  }'

```

### Remove tag from source template

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}/tags/{tag_name} \

  -H 'Authorization: Bearer <token>'

```

For complete tag management documentation, see [Template Tags](./tags.md).

## Related documentation

- [Template Tags](./tags.md) - Organize and filter templates with tags
- [Configuring Sources](./configuring-sources.md) - Create sources from templates
- [Connection Templates](./connection-templates.md) - Configure sync behavior
- [Authentication](./authentication.md) - Generate tokens for API access
