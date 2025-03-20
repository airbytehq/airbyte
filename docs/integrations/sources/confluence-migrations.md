# Confluence Migration Guide

## Upgrading to Version 1.0.0

With the release of **Confluence API V2**, several changes have been introduced to the connector, impacting endpoint structures and schema definitions. To ensure a seamless transition, follow the migration steps outlined below.

### Key Changes

- **Blog Posts:**  
  - **Endpoint Change:** `GET /content?type=blogpost` → `GET v2/blogposts`  
  - **Breaking Change:** Schema modifications require updating existing integrations.  

- **Pages:**  
  - **Endpoint Change:** `GET /content?type=page` → `GET v2/pages`  
  - **Breaking Change:** Schema modifications require adjustments.  

- **Spaces:**  
  - **Endpoint Change:** `GET /space` → `GET v2/spaces`  
  - **Breaking Change:** Schema updates necessitate migration.  

### Migration Steps

1. **Upgrade** to version **1.0.0**.  
2. **Resynchronize** the connector to reset schemas and update existing records.  

For more details, refer to the official **[Confluence API V2 Changelog](https://developer.atlassian.com/cloud/confluence/changelog/#CHANGE-2425)**.
