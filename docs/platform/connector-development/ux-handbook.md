import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Connector UX handbook

Use this handbook when you make decisions that affect how people configure or use connectors. Each form rule has a stable ID (for example, UX-01) so reviews and automated checks can link to it.

## Personas

| Persona | What you can expect |
| --- | --- |
| Data analyst | You use spreadsheets, SQL, and dashboards. You may not read API documentation, but you can follow clear steps to generate an API key. |
| Analytics engineer | You use SQL, `dbt`, Git, and a scripting language. You may know containers, but less about infrastructure than a data engineer. |
| Data engineer | You use SQL, `dbt`, multiple programming languages, cloud services, and orchestration tools. You build or consume APIs and manage infrastructure. |

The mix of personas varies by connector. A technical connector such as Kafka may have few data analysts.

## Guiding principles

Airbyte is infrastructure in a user's data pipeline. Users rely on it to move data securely, accurately, and reliably; they should not need to debug the infrastructure.

The hierarchy of user needs is security, data integrity, reliability, speed, ease of use, and feature set. Protect credentials and data, preserve records and their meaning, and make connectors reliable. Then optimize speed and usability while covering useful cases.

**Security** means protecting confidential data and credentials. Do not expose credentials in logs or plain text.

**Data integrity** means replicating complete and correct data. For example, preserve leading zeroes in postal codes and account for database time zones.

**Reliability** means handling large, unusual, and incorrectly formatted inputs without requiring users to debug the connector.

**Speed** reduces the time users wait for value and lets them iterate on configurations.

**Ease of use** means sensible defaults, predictable output, and little unnecessary friction.

**Feature set** means supporting as many useful cases as practical without making configuration harder to understand.

## How the connector form renders your spec

- **`required`**: Required fields appear in the main form. Optional fields are collapsed by default under **Optional fields**; `order` and `group` can affect how collapsed sections are arranged and labeled.
- **`default`**: The web application fills the form's initial values from schema defaults when it creates a configuration.
- **`order`**: Controls field ordering; required fields still precede optional fields.
- **`group`**: Places fields in a named group. The group title comes from the form's group metadata.
- **`always_show`**: Keeps an optional field expanded with the main form fields.
- **`airbyte_hidden`**: Hides a field from the form.
- **`oneOf`**: Renders a selector for the alternatives. Each option's `title` is its selector label.
- **`enum`**: Renders a dropdown for a scalar field.
- **`examples`**: Displays example values in the field's information panel.
- **`type: string` with `format: date` or `format: date-time`**: Renders a date picker; `date-time` includes a time control. `pattern` alone does not select the date picker.
- **`pattern` and `pattern_descriptor`**: `pattern` validates the value. `pattern_descriptor` displays a readable format hint beside the field.
- **`airbyte_secret`**: Uses a secret input that masks the value.

## Form rules

| ID | Rule |
| --- | --- |
| [UX-01](#ux-01) | Every field has a title and description |
| [UX-02](#ux-02) | Titles use sentence case |
| [UX-03](#ux-03) | Description says more than the title |
| [UX-04](#ux-04) | Required fields have a default when a safe value exists |
| [UX-05](#ux-05) | `pattern` has a readable `pattern_descriptor` |
| [UX-06](#ux-06) | Secrets marked `airbyte_secret` |
| [UX-07](#ux-07) | Fields with a default are required |
| [UX-08](#ux-08) | Explain meaning and impact |
| [UX-09](#ux-09) | Say where to get each value |
| [UX-10](#ux-10) | Doc links point to anchors |
| [UX-11](#ux-11) | Auth is not entirely optional |
| [UX-12](#ux-12) | Date pattern also sets `format: date`/`date-time` |

### UX-01: Every field has a title and description {#ux-01}

**Rule:** Give every user-facing field a clear `title` and `description`. The description should help the user understand what to enter.

**Why:** Without a title or description, users see a raw property name and have no explanation of the value.

**Exceptions:** A `oneOf` selector and its discriminator `const` fields do not need their own title and description.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (synthetic; the references for this rule are Python and Java):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      username:
        type: string
```

**Good (source-aws-cloudtrail):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      aws_region_name:
        type: string
        title: Region Name
        description: The default AWS Region to use.
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (source-gcs):**

```python
client_id: str = Field(title="Client ID", description="Client ID")
```

**Good (source-facebook-marketing):**

```python
client_id: str = Field(
    title="Client ID",
    description="Client ID for the Facebook Marketing API",
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (legacy spec.json, source-db2):**

```json
"host": {"description": "Host of the Db2.", "type": "string"}
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, source-mongodb-v2):**

```kotlin
@get:JsonSchemaTitle("Username")
@get:JsonPropertyDescription("The username which is used to access the database.")
val username: String
```

```json
"username": {"title": "Username", "type": "string", "description": "The username which is used to access the database."}
```

</TabItem>
</Tabs>

### UX-02: Titles use sentence case {#ux-02}

**Rule:** Write titles in sentence case: capitalize the first word and proper nouns, not every word. Keep product names and acronyms correctly capitalized.

**Why:** Sentence case makes field labels easier to scan and keeps the form consistent.

**Exceptions:** Preserve capitalization in product names and acronyms, such as “API key” and “Azure Blob Storage.”

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (synthetic; the ticket has no YAML reference for this rule):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      account_name:
        type: string
        title: Account Name
```

**Good (synthetic):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      account_name:
        type: string
        title: Account name
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (source-facebook-marketing):**

```python
access_token: str = Field(title="Access Token")
```

**Good (synthetic Pydantic example):**

```python
account_name: str = Field(title="Account name")
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (legacy spec.json, source-postgres):**

```json
"database": {"title": "Database Name"}
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, source-postgres):**

```kotlin
@get:JsonSchemaTitle("CA certificate")
val sslCertificate: String
```

```json
"ca_certificate": {"title": "CA certificate"}
```

</TabItem>
</Tabs>

### UX-03: Description says more than the title {#ux-03}

**Rule:** Explain the field's purpose in its description instead of repeating its title. Add context that helps the user choose a value.

**Why:** A description that repeats the label does not help users decide what to enter.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-linkedin-ads):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        title: Lookback Window
        description: How far into the past to look for records. (in days)
```

**Good (source-bing-ads):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        title: Lookback window
        description: Also known as attribution or conversion window. How far into the past to look for records (in days).
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (source-gcs):**

```python
client_secret: str = Field(title="Client Secret", description="Client Secret")
```

**Good (source-facebook-marketing):**

```python
client_id: str = Field(
    title="Client ID",
    description="Client ID for the Facebook Marketing API",
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (legacy spec.json, source-postgres):**

```json
"ca_certificate": {"title": "CA certificate", "description": "CA certificate"}
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, source-bigquery):**

```kotlin
@JsonSchemaTitle("Project ID")
@JsonSchemaDescription("The GCP project ID for the project containing the BigQuery datasets to read from.")
lateinit var projectId: String
```

```json
"project_id": {"title": "Project ID", "description": "The GCP project ID for the project containing the target BigQuery dataset."}
```

</TabItem>
</Tabs>

### UX-04: Required fields have a default when a safe value exists {#ux-04}

**Rule:** Give required fields a default when a safe value exists. A common region or `is_sandbox: false` can be a safe default; never default credentials or IDs.

**Why:** A safe default pre-fills the form and saves users from choosing a value that works for most configurations.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (synthetic):**

```yaml
spec:
  connection_specification:
    type: object
    required: [aws_region_name]
    properties:
      aws_region_name: {type: string, title: Region}
```

**Good (source-aws-cloudtrail):**

```yaml
spec:
  connection_specification:
    type: object
    required: [aws_region_name]
    properties:
      aws_region_name: {type: string, title: Region Name, default: us-east-1}
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (synthetic required field with no safe default):**

```python
project_id: str = Field(..., title="Project ID")
```

**Good (synthetic Pydantic schema metadata; the table's Python reference does not use Pydantic):**

```python
class SourceSpec(BaseModel):
    region: str = Field(..., title="Region")

    class Config:
        @staticmethod
        def schema_extra(schema, model):
            schema["properties"]["region"]["default"] = "us-east-1"
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (synthetic legacy spec.json):**

```json
"required": ["region"],
"region": {"type": "string"}
```

**Good (synthetic Kotlin bulk CDK annotation and legacy spec.json based on destination-salesforce):**

```kotlin
@get:JsonProperty("is_sandbox")
@get:JsonSchemaInject(json = """{"default":false}""")
var isSandbox: Boolean = false
```

```json
"required": ["is_sandbox"],
"is_sandbox": {"type": "boolean", "default": false}
```

</TabItem>
</Tabs>

### UX-05: `pattern` has a readable `pattern_descriptor` {#ux-05}

**Rule:** When you validate a value with `pattern`, provide a readable `pattern_descriptor`. Describe the expected format rather than relying on users to interpret a regular expression.

**Why:** The form shows a readable hint beside the field when `pattern_descriptor` is set or the web application recognizes the pattern. An explicit descriptor keeps other patterns understandable.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-amazon-seller-partner; a web application fallback applies):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      replication_end_date:
        type: string
        pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$|^$
```

**Good (synthetic manifest excerpt based on the source-google-ads spec):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      start_date:
        type: string
        pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
        pattern_descriptor: YYYY-MM-DD
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (synthetic):**

```python
start_date: str = Field(
    ...,
    pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]+$",
)
```

**Good (synthetic, using the `Field` extra-key style in source-facebook-marketing):**

```python
start_date: str = Field(
    ...,
    pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
    pattern_descriptor="YYYY-MM-DD",
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (legacy spec.json, destination-clickhouse):**

```json
"cluster_name": {"pattern": "^[a-zA-Z0-9_-]+$"}
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, synthetic):**

```kotlin
@get:JsonSchemaInject(json = """{"pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}$","pattern_descriptor":"YYYY-MM-DD"}""")
val startDate: String
```

```json
"start_date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$", "pattern_descriptor": "YYYY-MM-DD"}
```

</TabItem>
</Tabs>

### UX-06: Secrets marked `airbyte_secret` {#ux-06}

**Rule:** Mark every secret field with `airbyte_secret: true`. Do not mark public values, IDs, or other non-secret fields as secrets.

**Why:** Unmarked credentials appear in a regular text control instead of a masked secret control.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (`source-100ms`):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      app_access_key:
        type: string
        title: App Access Key
```

**Good (source-aws-cloudtrail):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      aws_secret_key:
        type: string
        title: Secret Key
        airbyte_secret: true
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (synthetic variant of a source-facebook-marketing credential):**

```python
client_secret: str = Field(title="Client Secret", description="Client Secret for the Facebook Marketing API")
```

**Good (source-facebook-marketing):**

```python
client_secret: str = Field(
    title="Client Secret",
    description="Client Secret for the Facebook Marketing API",
    airbyte_secret=True,
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (synthetic legacy spec.json):**

```json
"api_key": {"type": "string", "title": "API key"}
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, source-mssql):**

```kotlin
@JsonSchemaTitle("Password")
@JsonSchemaInject(json = """{"airbyte_secret":true}""")
var password: String? = null
```

```json
"password": {"type": "string", "title": "Password", "airbyte_secret": true}
```

</TabItem>
</Tabs>

### UX-07: Fields with a default are required {#ux-07}

**Rule:** If a field has a default, add it to the parent's list of required properties. This ensures every saved configuration contains the value that determines the connector's behavior.

**Why:** A defaulted optional field can stay collapsed under **Optional fields**, and configurations created through APIs or Terraform do not get defaults filled in by the web application.

:::note Coming soon
Do not move existing optional fields with defaults into `required` yet. Today, required fields always show in the main form. Making an existing field required is a breaking change because API and Terraform updates of saved configurations that lack the field fail validation.
:::

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-amazon-seller-partner):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      num_workers:
        type: integer
        default: 2
```

**Good (source-aws-cloudtrail):**

```yaml
spec:
  connection_specification:
    type: object
    required: [aws_region_name]
    properties:
      aws_region_name: {type: string, default: us-east-1}
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (source-facebook-marketing):**

```python
time_increment: Optional[PositiveInt] = Field(default=1, title="Time Increment")
```

**Good (synthetic Pydantic schema metadata):**

```python
class SourceSpec(BaseModel):
    region: str = Field(..., title="Region")

    class Config:
        @staticmethod
        def schema_extra(schema, model):
            schema["properties"]["region"]["default"] = "us-east-1"
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (legacy spec.json, source-mongodb-v2):**

```json
"discover_timeout_seconds": {"type": "integer", "default": 600}
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, destination-mssql):**

```kotlin
@get:JsonSchemaInject(json = """{"default":"public"}""")
val schema: String = "public"
```

```json
"required": ["schema"],
"schema": {"type": "string", "default": "public"}
```

</TabItem>
</Tabs>

### UX-08: Explain meaning and impact {#ux-08}

**Rule:** Explain what a field controls and how changing it affects the data, sync, or output. Give users enough context to choose a value.

**Why:** A vague label or short description leaves users guessing about the effect of a setting.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-linkedin-ads):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        description: How far into the past to look for records. (in days)
```

**Good (source-bing-ads):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        description: Also known as attribution or conversion window. How far into the past to look for records (in days). Used only for performance report streams in incremental mode without specified Reports Start Date.
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (synthetic):**

```python
lookback_window: Optional[PositiveInt] = Field(title="Lookback window", description="How far back to look.")
```

**Good (source-facebook-marketing):**

```python
insights_lookback_window: Optional[PositiveInt] = Field(
    title="Insights Lookback Window",
    description=(
        "The attribution window. Facebook freezes insight data 28 days after it was generated, "
        "which means that all data from the past 28 days may have changed since we last emitted it, "
        "so you can retrieve refreshed insights from the past by setting this parameter."
    ),
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (Kotlin source-postgres):**

```kotlin
@JsonSchemaTitle("CA certificate")
@JsonPropertyDescription("CA certificate")
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, source-bigquery):**

```kotlin
@JsonSchemaTitle("Service Account Key JSON")
@JsonSchemaDescription("The contents of the JSON service account key.")
lateinit var credentialsJson: String
```

```json
"credentials_json": {"title": "Credentials JSON", "description": "The contents of your Service Account Key JSON file."}
```

</TabItem>
</Tabs>

### UX-09: Say where to get each value {#ux-09}

**Rule:** Tell users where to find each value they must provide. Link to setup instructions when they can explain the steps.

**Why:** Users should not have to search a vendor's site or guess which credential or identifier you need.

**Exceptions:** Do not apply this rule to fields OAuth fills in through `advanced_auth.complete_oauth_output_specification`.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-gong):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      access_key:
        title: Gong Access Key
        description: Gong Access Key
```

**Good (source-amplitude):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      api_key:
        title: API Key
        description: See the <a href="https://docs.airbyte.com/integrations/sources/amplitude#setup-guide">setup guide</a> for how to obtain this key.
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (synthetic):**

```python
client_secret: str = Field(title="Client secret", description="Client secret")
```

**Good (source-facebook-marketing):**

```python
access_token: Optional[str] = Field(
    title="Access Token",
    description="Generate a Meta system user access token in Meta Business Settings > Users > System users.",
    airbyte_secret=True,
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (legacy spec.json, source-dynamodb):**

```json
"access_key_id": {"title": "Dynamodb Key Id", "type": "string"}
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, source-bigquery):**

```kotlin
@JsonSchemaDescription("Check out the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">docs</a> if you need help generating this key.")
lateinit var credentialsJson: String
```

```json
"credentials_json": {"description": "See the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#setup-the-bigquery-source-in-airbyte\">docs</a> for how to obtain this key."}
```

</TabItem>
</Tabs>

### UX-10: Doc links point to anchors {#ux-10}

**Rule:** Link to the relevant heading or setup section when a page has one. Use a stable, current URL rather than sending users to a page's top-level overview.

**Why:** An anchored link takes users directly to the instructions they need.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-hubspot):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      credentials:
        description: See the <a href="https://legacydocs.hubspot.com/docs/methods/oauth2/oauth2-quickstart">HubSpot docs</a>.
```

**Good (source-amplitude):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      api_key:
        description: See the <a href="https://docs.airbyte.com/integrations/sources/amplitude#setup-guide">setup guide</a>.
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (source-facebook-marketing):**

```python
description="See the <a href=\"https://docs.airbyte.com/integrations/sources/facebook-marketing\">docs</a>."
```

**Good (synthetic Field snippet with a section link):**

```python
description="See the <a href=\"https://docs.airbyte.com/integrations/sources/amplitude#setup-guide\">setup guide</a>."
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (legacy spec.json, source-dynamodb):**

```json
"description": "See the AWS documentation."
```

**Good (Kotlin bulk CDK annotation and legacy spec.json, source-bigquery):**

```kotlin
@JsonSchemaDescription("See the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">service account key instructions</a>.")
```

```json
"description": "See the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#setup-the-bigquery-source-in-airbyte\">setup instructions</a>."
```

</TabItem>
</Tabs>

### UX-11: Auth is not entirely optional {#ux-11}

**Rule:** Put the method selector (`credentials`) in the top-level `required` list and define one `oneOf` option per authentication method. If anonymous access is supported, represent **No auth** as an explicit option rather than making the selector optional; GitHub, HubSpot, and Jira manifests demonstrate required selectors with method options.

**Why:** If the selector is optional, users can save a configuration without choosing or providing an authentication method.

**Exceptions:** Deliberately optional credentials, such as a public API key or a database password that can be omitted, are still reported. You can ignore the finding when the connector intentionally supports that configuration.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-airtable):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      credentials:
        type: object
        oneOf: [{title: OAuth}, {title: Personal Access Token}]
```

**Good (synthetic method selector based on source-github):**

```yaml
spec:
  connection_specification:
    type: object
    required: [credentials]
    properties:
      credentials:
        type: object
        oneOf:
          - {title: API key}
          - {title: No auth}
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (synthetic optional selector):**

```python
credentials: Optional[Union[ApiKey, NoAuth]] = Field(None, title="Authentication")
```

**Good (synthetic Pydantic pattern used by source-facebook-marketing):**

```python
credentials: Union[ApiKey, NoAuth] = Field(..., title="Authentication", type="object", discriminator="auth_type")
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (synthetic legacy spec.json):**

```json
"properties": {"credentials": {"type": "object", "oneOf": [{"title": "API key"}]}}
```

**Good (synthetic Kotlin bulk-CDK type and legacy spec.json):**

```kotlin
@JsonSchemaTitle("Authentication")
sealed class Credentials
```

```json
"required": ["credentials"],
"credentials": {"type": "object", "oneOf": [{"title": "API key"}, {"title": "No auth"}]}
```

</TabItem>
</Tabs>

### UX-12: Date pattern also sets `format: date`/`date-time` {#ux-12}

**Rule:** For a date or date-time field, set `type: string`, the matching `format`, and a `pattern` with a readable `pattern_descriptor`. Use `date` for a date and `date-time` when the value includes a time.

**Why:** The date picker requires the string type and date format. A pattern without a format renders a plain text field.

**Examples:** Compare poor and good snippets in each language tab.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML (manifest)">

**Poor (source-apple-search-ads):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      start_date:
        type: string
        pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
```

**Good (synthetic; the ticket's good reference is source-google-ads):**

```yaml
spec:
  connection_specification:
    type: object
    properties:
      start_date:
        type: string
        format: date
        pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
        pattern_descriptor: YYYY-MM-DD
      created_at:
        type: string
        format: date-time
        pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$
        pattern_descriptor: YYYY-MM-DDTHH:mm:ssZ
```

</TabItem>
<TabItem value="python" label="Python">

**Poor (synthetic):**

```python
start_date: str = Field(..., pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
```

**Good (synthetic Pydantic `Field` extra keys):**

```python
start_date: str = Field(
    ...,
    format="date",
    pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
    pattern_descriptor="YYYY-MM-DD",
)
created_at: str = Field(
    ...,
    format="date-time",
    pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
    pattern_descriptor="YYYY-MM-DDTHH:mm:ssZ",
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

**Poor (synthetic; the ticket has no Java date-pattern example):**

```json
"start_date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
```

**Good (synthetic Kotlin bulk-CDK annotation and legacy spec.json):**

```kotlin
@get:JsonSchemaInject(json = """{"format":"date","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}$","pattern_descriptor":"YYYY-MM-DD"}""")
val startDate: String
@get:JsonSchemaInject(json = """{"format":"date-time","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$","pattern_descriptor":"YYYY-MM-DDTHH:mm:ssZ"}""")
val createdAt: String
```

```json
"start_date": {"type": "string", "format": "date", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$", "pattern_descriptor": "YYYY-MM-DD"},
"created_at": {"type": "string", "format": "date-time", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", "pattern_descriptor": "YYYY-MM-DDTHH:mm:ssZ"}
```

</TabItem>
</Tabs>

## Other form guidance

Configuration adds work and creates opportunities for confusion. Avoid asking users to configure a behavior when the connector can choose a safe value or handle it automatically. Avoid exposing implementation details such as retry counts unless users need them to reach a goal.

Use `order` and `group` to arrange related fields. Keep technical or niche options out of the main flow with collapsed groups, and use `always_show` only when users need to see an optional field immediately. Give every `oneOf` option a `title`, add useful `examples`, and use `enum` instead of free text when the accepted values are fixed.

Fail fast and provide an actionable error. Use `pattern` to reject malformed values and `pattern_descriptor` to explain the expected format. See [UX-05](https://docs.airbyte.com/platform/connector-development/ux-handbook#ux-05) and [UX-12](https://docs.airbyte.com/platform/connector-development/ux-handbook#ux-12).

## Output data and schemas

### Strongly favor ELT over ETL

Extract-load-transform (ELT) means extracting and loading the data into a destination while leaving its format and schema as unchanged as possible, and making transformation the responsibility of the consumer. By contrast, ETL means transforming data before it is sent to the destination, for example changing its schema to make it easier to consume in the destination.

When extracting data, strongly prefer ELT to ETL for the following reasons:

#### Removes Airbyte as a development bottleneck

If we get into the habit of structuring the output of each source according to how some users want to use it, then we will invite more feature requests from users asking us to transform data in a particular way. This introduces Airbyte’s development team as an unnecessary bottleneck for these users.

Instead, we should set the standard that a user should be responsible for transformations once they’ve loaded data in a destination.

#### Will always be backwards compatible

APIs already follow strong conventions to maintain backwards compatibility. By transforming data, we break this guarantee, which means we may break downstream flows for our users.

#### Future proof

We may have a vision of what a user needs today. But if our persona evolves next year, then we’ll probably also need to adapt our transformation logic, which would require significant development and data migration efforts.

#### More flexible

Current users have different needs from data. By being opinionated on how they should consume data, we are effectively favoring one user persona over the other. While there might be some cases where this is warranted, it should be done with extreme intentionality.

#### More efficient

With ETL, if the “T” ever needs to change, then we need to re-extract all data for all users. This is computationally and financially expensive and will place a lot of pressure on the source systems as we re-extract all data.

### Describe output schemas as completely and reliably as possible

Our most popular destinations are strongly typed like Postgres, BigQuery, Parquet, and `Avro`.

Being strongly typed enables optimizations and syntactic sugar to make it very easy and efficient for the user to query data.

To provide the best UX when moving data to these destinations, Airbyte source connectors should describe their schema in as much detail as correctness allows.

In some cases, describing schemas is impossible to do reliably. For example, MongoDB doesn’t have any schemas. To infer the schema, one needs to read all the records in a particular table. And even then, once new records are added, they also must all be read in order to update the inferred schema. At the time of writing, this is infeasible to do efficiently in Airbyte since we do not have an intermediate staging area to do this. In this case, we should do the “best we can” to describe the schema, keeping in mind that reliability of the described schema is more important than expressiveness.

That is, we would rather not describe a schema at all than describe it incorrectly, as incorrect descriptions **will** lead to failures downstream.

To keep schema descriptions reliable, [automate schema generation](https://docs.airbyte.com/platform/connector-development/cdk-python/schemas#generating-schemas-from-openapi-definitions) whenever possible.

### Be very cautious about breaking changes to output schemas

Assuming we follow ELT over ETL, and automate generation of output schemas, this should come up very rarely. However, it is still important enough to warrant mention.

If for any reason we need to change the output schema declared by a connector in a backwards breaking way, consider it a necessary evil that should be avoided if possible. Basically, the only reasons for a backwards breaking change should be:

- A connector previously had an incorrect schema.
- A connector was not following ELT principles and is now being changed to follow them.

Other breaking changes should probably be escalated for approval.

## Prerequisite configurations and assumptions

### Document all assumptions

If a connector makes assumptions about the underlying data source, then these assumptions must be documented. For example: for some features of the Facebook Pages connector to work, a user must have an Instagram Business account linked to an Instagram page linked to their Facebook Page. In this case, the externally facing documentation page for the connector must be very clear about this.

### Provide how-tos for prerequisite configuration

If a user needs to set up their data source in a particular way to pull data, then we must provide documentation for how they should do it.

For example, to set up CDC for databases, a user must create logical replication slots and do a few other things. These steps should be documented with examples or screenshots wherever possible (e.g: here are the SQL statements you need to run, with the following permissions, on the following screen, etc.)

## External documentation

This section is concerned with the external-facing documentation of a connector that goes in [https://docs.airbyte.com](https://docs.airbyte.com) e.g: [this one](https://docs.airbyte.com/integrations/sources/amazon-seller-partner)

### Documentation should communicate persona-impacting behaviors

When writing documentation ask: who is the intended target persona for a piece of documentation, and what information do they need to understand how this connector impacts their workflows?

For example, data analysts & analytics engineers probably don’t care if we use `Debezium` for database replication. To them, the important thing is that we provide Change Data Capture (CDC) -- `Debezium` is an implementation detail. Therefore, when communicating information about our database replication logic, we should emphasize the end behaviors, rather than implementation details.

**Example**: Don’t say: “`Debezium` cannot process UTF-16 character set“.

Instead, say: “When using CDC, UTF-16 characters are not currently supported”

A user who doesn’t already know what `Debezium` is might be left confused by the first phrasing, so we should use the second phrasing.
