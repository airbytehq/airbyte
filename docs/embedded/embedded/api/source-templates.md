# Source Templates

Source Templates define which sources are available for your users. They represent Airbyte Sources. with optionally pre-configured fields to streamline their setup.

The Airbyte platform comes with ready to use templates. You can also create templates specific to your organization if you need access to more integrations or if you want different default values.

Here is an example request to create a new template using only default values
```
curl https://api.airbyte.ai/api/v1/integrations/sources\
-H 'authorization: Bearer <token>'
-H 'content-type: application/json' \
--data-raw '{"organization_id":"<organization_id>","actor_definition_id":"<definition_id>","partial_default_config":{}, "additional_required_parameters": []}' -vvv
```

You can find the actor definition ID from the [Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

The partial_default_config is a JSON object representing keys from the connector spec for which you want to set default values so your users don't need to set them up themselves.