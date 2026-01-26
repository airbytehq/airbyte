# Template Tags

## Overview

Template tags are a powerful tool through which you can configure available source and connection templates for use in a specific workspace. They are strings you can include in the template itself that serve as filters via the widget token. By including `selected_source_template_tags` and `selected_connection_template_tags` you define the source and connection templates available in the corresponding workspace's widget. Examples of workflows available via template tags are:

- Assigning unique and separate destinations by customer's workspace.
- Offering a specific source packages to different customer segments.
- Organizing available source templates by data type (e.g. "Analytics", "CRM", "Cloud Storage")

## Creating Tags

You can create a tag on your source or connection templates either programmatically or via [our newly released UI](https://app.airbyte.ai).

<img width="936" height="261" alt="Screenshot 2025-09-17 at 9 44 28 PM" src="https://github.com/user-attachments/assets/aebc08af-e922-4cf8-b35f-b5880d57a1f3" />


To programmatically create a tag for a connection template, you'll need to make the following request.

``` bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}/tag" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "X-Organization-Id: <ORGANIZATION_ID>" \
  -H "Content-Type: application/json" \
  -d '{"tag": "your-tag-name"}'
```

To programmatically create a tag for a source template, you'll need to make the following request.

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}/tag" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "X-Organization-Id: <ORGANIZATION_ID>" \
  -H "Content-Type: application/json" \
  -d '{"tag": "your-tag-name"}'
```

## Filtering and Removing Tags

When you embed the Airbyte widget in your front-end, you generate a widget token. This token is passed to the widget and controls which source and connection templates are available, based on the tag specifications.
The widget token is created with parameters like ‎`selected_source_template_tags` and ‎`selected_connection_template_tags_mode`, which define what the end user can see and select in your web application.

Additionally, you can untag connnection and source templates via the same UI presented above or programmatically.

To programmatically remove a tag from a connection template, you'll need to make the following request:

```bash
curl -X DELETE "https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}/tag/{tag_name}" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "X-Organization-Id: <ORGANIZATION_UUID>"
```

To programmatically remove a tag from a source template, you'll need to make the following request:

```bash 
curl -X DELETE "https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}/tag/{tag_name}" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "X-Organization-Id: <ORGANIZATION_UUID>"
```

If you have any questions on enabling and registering these tags, please reach out to the team.
