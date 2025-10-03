---
products: embedded
---

# Source Templates

A source template controls which connectors appear in the Embedded widget and how their config screens look. When a customer opens the widget, only the sources backed by a template are selectable—so you can pre‑set sensible defaults or restrict advanced settings.

The Airbyte platform comes with ready to use templates. You can also create templates specific to your organization if you need access to more integrations or if you want different default values.

Here is an example request to create a new template using only default values
```
curl https://api.airbyte.ai/api/v1/integrations/templates/sources \
-H 'authorization: Bearer <token>' \
-H 'content-type: application/json' \
--data-raw '{
  "organization_id": "7c60d51f-b44e-4682-87d6-449835ea4de6",
  "actor_definition_id": "45b7d7e6-d7d5-4f31-8c1a-9fd96ce6ee35",
  "partial_default_config": {}
}' -vvv
```

You can find the actor definition ID from the [Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

The partial_default_config is a JSON object representing keys from the connector spec for which you want to set default values so your users don't need to set them up themselves.

# Deleting Templates
 
You can delete Source Templates by submitting a DELETE request to the API:

```
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}' \
-H 'authorization: Bearer <token>'
```

Sources created from a deleted Source Template will stop showing up in the Widget.

When a Source Template is updated, all existing Sources created from it will also be updated.

# Listing Templates
The [List Source Templates endpoint](https://api.airbyte.ai/api/v1/docs#tag/Template-Sources/operation/list_integrations_templates_sources) lists both the templates you created, as well as standard templates that are available to everyone using the platform.
