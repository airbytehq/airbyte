---
id: airbyte_agent_sdk-connectors-intercom-index
title: airbyte_agent_sdk.connectors.intercom.index
---

Module airbyte_agent_sdk.connectors.intercom
============================================
Intercom connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.intercom.connector
* airbyte_agent_sdk.connectors.intercom.connector_model
* airbyte_agent_sdk.connectors.intercom.models
* airbyte_agent_sdk.connectors.intercom.types

Classes
-------

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[CompaniesSearchData]
    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[ConversationsSearchData]
    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[TeamsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="CompaniesSearchResult"></a>

`CompaniesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ContactsSearchResult"></a>

`ContactsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ConversationsSearchResult"></a>

`ConversationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TeamsSearchResult"></a>

`TeamsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CompaniesSearchData"></a>

`CompaniesSearchData(**data: Any)`
:   Search result data for companies entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: str | None`
    :   The ID of the application associated with the company

    `company_id: str | None`
    :   The unique identifier of the company

    `created_at: int | None`
    :   The date and time when the company was created

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes specific to the company

    `id: str | None`
    :   The ID of the company

    `industry: str | None`
    :   The industry in which the company operates

    `model_config`
    :   The type of the None singleton.

    `monthly_spend: float | None`
    :   The monthly spend of the company

    `name: str | None`
    :   The name of the company

    `plan: dict[str, typing.Any] | None`
    :   Details of the company's subscription plan

    `remote_created_at: int | None`
    :   The remote date and time when the company was created

    `segments: dict[str, typing.Any] | None`
    :   Segments associated with the company

    `session_count: int | None`
    :   The number of sessions related to the company

    `size: int | None`
    :   The size of the company

    `tags: dict[str, typing.Any] | None`
    :   Tags associated with the company

    `type_: str | None`
    :   The type of the company

    `updated_at: int | None`
    :   The date and time when the company was last updated

    `user_count: int | None`
    :   The number of users associated with the company

    `website: str | None`
    :   The website of the company

<a id="ContactsSearchData"></a>

`ContactsSearchData(**data: Any)`
:   Search result data for contacts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `android_app_name: str | None`
    :   The name of the Android app associated with the contact.

    `android_app_version: str | None`
    :   The version of the Android app associated with the contact.

    `android_device: str | None`
    :   The device used by the contact for Android.

    `android_last_seen_at: str | None`
    :   The date and time when the contact was last seen on Android.

    `android_os_version: str | None`
    :   The operating system version of the Android device.

    `android_sdk_version: str | None`
    :   The SDK version of the Android device.

    `avatar: str | None`
    :   URL pointing to the contact's avatar image.

    `browser: str | None`
    :   The browser used by the contact.

    `browser_language: str | None`
    :   The language preference set in the contact's browser.

    `browser_version: str | None`
    :   The version of the browser used by the contact.

    `companies: dict[str, typing.Any] | None`
    :   Companies associated with the contact.

    `created_at: int | None`
    :   The date and time when the contact was created.

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes defined for the contact.

    `email: str | None`
    :   The email address of the contact.

    `external_id: str | None`
    :   External identifier for the contact.

    `has_hard_bounced: bool | None`
    :   Flag indicating if the contact has hard bounced.

    `id: str | None`
    :   The unique identifier of the contact.

    `ios_app_name: str | None`
    :   The name of the iOS app associated with the contact.

    `ios_app_version: str | None`
    :   The version of the iOS app associated with the contact.

    `ios_device: str | None`
    :   The device used by the contact for iOS.

    `ios_last_seen_at: int | None`
    :   The date and time when the contact was last seen on iOS.

    `ios_os_version: str | None`
    :   The operating system version of the iOS device.

    `ios_sdk_version: str | None`
    :   The SDK version of the iOS device.

    `language_override: str | None`
    :   Language override set for the contact.

    `last_contacted_at: int | None`
    :   The date and time when the contact was last contacted.

    `last_email_clicked_at: int | None`
    :   The date and time when the contact last clicked an email.

    `last_email_opened_at: int | None`
    :   The date and time when the contact last opened an email.

    `last_replied_at: int | None`
    :   The date and time when the contact last replied.

    `last_seen_at: int | None`
    :   The date and time when the contact was last seen overall.

    `location: dict[str, typing.Any] | None`
    :   Location details of the contact.

    `marked_email_as_spam: bool | None`
    :   Flag indicating if the contact's email was marked as spam.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the contact.

    `notes: dict[str, typing.Any] | None`
    :   Notes associated with the contact.

    `opted_in_subscription_types: dict[str, typing.Any] | None`
    :   Subscription types the contact opted into.

    `opted_out_subscription_types: dict[str, typing.Any] | None`
    :   Subscription types the contact opted out from.

    `os: str | None`
    :   Operating system of the contact's device.

    `owner_id: int | None`
    :   The unique identifier of the contact's owner.

    `phone: str | None`
    :   The phone number of the contact.

    `referrer: str | None`
    :   Referrer information related to the contact.

    `role: str | None`
    :   Role or position of the contact.

    `signed_up_at: int | None`
    :   The date and time when the contact signed up.

    `sms_consent: bool | None`
    :   Consent status for SMS communication.

    `social_profiles: dict[str, typing.Any] | None`
    :   Social profiles associated with the contact.

    `tags: dict[str, typing.Any] | None`
    :   Tags associated with the contact.

    `type_: str | None`
    :   Type of contact.

    `unsubscribed_from_emails: bool | None`
    :   Flag indicating if the contact unsubscribed from emails.

    `unsubscribed_from_sms: bool | None`
    :   Flag indicating if the contact unsubscribed from SMS.

    `updated_at: int | None`
    :   The date and time when the contact was last updated.

    `utm_campaign: str | None`
    :   Campaign data from UTM parameters.

    `utm_content: str | None`
    :   Content data from UTM parameters.

    `utm_medium: str | None`
    :   Medium data from UTM parameters.

    `utm_source: str | None`
    :   Source data from UTM parameters.

    `utm_term: str | None`
    :   Term data from UTM parameters.

    `workspace_id: str | None`
    :   The unique identifier of the workspace associated with the contact.

<a id="ConversationsSearchData"></a>

`ConversationsSearchData(**data: Any)`
:   Search result data for conversations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_assignee_id: int | None`
    :   The ID of the administrator assigned to the conversation

    `ai_agent: dict[str, typing.Any] | None`
    :   Data related to AI Agent involvement in the conversation

    `ai_agent_participated: bool | None`
    :   Indicates whether AI Agent participated in the conversation

    `assignee: dict[str, typing.Any] | None`
    :   The assigned user responsible for the conversation.

    `contacts: dict[str, typing.Any] | None`
    :   List of contacts involved in the conversation.

    `conversation_message: dict[str, typing.Any] | None`
    :   The main message content of the conversation.

    `conversation_rating: dict[str, typing.Any] | None`
    :   Ratings given to the conversation by the customer and teammate.

    `created_at: int | None`
    :   The timestamp when the conversation was created

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes associated with the conversation

    `customer_first_reply: dict[str, typing.Any] | None`
    :   Timestamp indicating when the customer first replied.

    `customers: list[typing.Any] | None`
    :   List of customers involved in the conversation

    `first_contact_reply: dict[str, typing.Any] | None`
    :   Timestamp indicating when the first contact replied.

    `id: str | None`
    :   The unique ID of the conversation

    `linked_objects: dict[str, typing.Any] | None`
    :   Linked objects associated with the conversation

    `model_config`
    :   The type of the None singleton.

    `open: bool | None`
    :   Indicates if the conversation is open or closed

    `priority: str | None`
    :   The priority level of the conversation

    `read: bool | None`
    :   Indicates if the conversation has been read

    `redacted: bool | None`
    :   Indicates if the conversation is redacted

    `sent_at: int | None`
    :   The timestamp when the conversation was sent

    `sla_applied: dict[str, typing.Any] | None`
    :   Service Level Agreement details applied to the conversation.

    `snoozed_until: int | None`
    :   Timestamp until the conversation is snoozed

    `source: dict[str, typing.Any] | None`
    :   Source details of the conversation.

    `state: str | None`
    :   The state of the conversation (e.g., new, in progress)

    `statistics: dict[str, typing.Any] | None`
    :   Statistics related to the conversation.

    `tags: dict[str, typing.Any] | None`
    :   Tags applied to the conversation.

    `team_assignee_id: int | None`
    :   The ID of the team assigned to the conversation

    `teammates: dict[str, typing.Any] | None`
    :   List of teammates involved in the conversation.

    `title: str | None`
    :   The title of the conversation

    `topics: dict[str, typing.Any] | None`
    :   Topics associated with the conversation.

    `type_: str | None`
    :   The type of the conversation

    `updated_at: int | None`
    :   The timestamp when the conversation was last updated

    `user: dict[str, typing.Any] | None`
    :   The user related to the conversation.

    `waiting_since: int | None`
    :   Timestamp since waiting for a response

<a id="IntercomAuthConfig"></a>

`IntercomAuthConfig(**data: Any)`
:   Access Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Your Intercom API Access Token

    `model_config`
    :   The type of the None singleton.

<a id="IntercomConnector"></a>

`IntercomConnector(auth_config: IntercomAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Intercom API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new intercom connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., IntercomAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = IntercomConnector(auth_config=IntercomAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = IntercomConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = IntercomConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'IntercomAuthConfig'", name: str | None = None, replication_config: "'IntercomReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A IntercomConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await IntercomConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=IntercomAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await IntercomConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=IntercomAuthConfig(access_token="..."),
                replication_config=IntercomReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @IntercomConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @IntercomConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await IntercomConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            IntercomCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

<a id="IntercomReplicationConfig"></a>

`IntercomReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Intercom.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.

<a id="TeamsSearchData"></a>

`TeamsSearchData(**data: Any)`
:   Search result data for teams entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_ids: list[typing.Any] | None`
    :   Array of user IDs representing the admins of the team.

    `id: str | None`
    :   Unique identifier for the team.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the team.

    `type_: str | None`
    :   Type of team (e.g., 'internal', 'external').