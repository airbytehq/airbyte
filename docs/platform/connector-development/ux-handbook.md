import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Connector UX handbook

Use this handbook when you make decisions that affect how people configure or use connectors. Each form rule has a stable ID (for example, UX-01) so reviews and automated checks can link to it.

## Personas

| Persona | What you can expect |
| --- | --- |
| Data analyst | Uses spreadsheets, SQL, and dashboards. May not read API documentation, but can follow clear steps to generate an API key. |
| Analytics engineer | Uses SQL, `dbt`, Git, and a scripting language. May know containers, but less about infrastructure than a data engineer. |
| Data engineer | Uses SQL, `dbt`, multiple programming languages, cloud services, and orchestration tools. Builds or consumes APIs and manages infrastructure. |

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

- **`required`**: Required fields appear in the main form. Root-level optional fields without `order` collapse into **Optional fields** at the end of the form. Optional fields with `order`, and nested optional fields, collapse in place.
- **`default`**: When the web app creates a new configuration, it fills initial form values from schema defaults. API, Terraform, and PyAirbyte callers do not receive defaults from the web app.
- **`order`**: Orders fields within their required or optional sections; required fields still precede optional fields.
- **`group`**: Places root-level fields in a named group. Group titles come from the form's group metadata.
- **`always_show`**: Keeps an optional field expanded with the main form fields.
- **`airbyte_hidden`**: Hides a field from the form.
- **`oneOf`**: Renders a selector for the alternatives. Each option's `title` is its selector label. `oneOf` blocks and groups other than resource allocation are always expanded.
- **`enum`**: Renders a dropdown for a scalar field.
- **`examples`**: Displays example values next to the field's description when users open the field's info icon.
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

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      data_format:
        type: string
        enum: [csv, json]
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    properties:
      aws_region_name:
        type: string
        title: AWS region
        description: AWS region in which CloudTrail stores trail events. Choose the region used by your trail in the AWS console.
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
max_retries: Optional[PositiveInt] = Field(...)
```

```python title="Good"
access_token: Optional[str] = Field(
    title="Access token",
    description="Generate a Meta system user access token in Meta Business Settings > Users > System users > Generate new token for your app.",
    airbyte_secret=True,
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```json title="Poor"
{
  "properties": {
    "query_timeout_seconds": {
      "type": "integer",
      "description": "Timeout in seconds before the connector cancels a query."
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("database")
@JsonSchemaTitle("Database name")
@JsonPropertyDescription("Name of the database that contains the tables to replicate. Enter the name shown in your database management console.")
lateinit var database: String
```

```json title="Good: spec.json"
{
  "required": ["database"],
  "properties": {
    "database": {
      "type": "string",
      "title": "Database name",
      "description": "Name of the database that contains the tables to replicate. Enter the name shown in your database management console."
    }
  }
}
```

</TabItem>
</Tabs>

### UX-02: Titles use sentence case {#ux-02}

**Rule:** Write titles in sentence case: capitalize the first word and proper nouns, not every word. Keep product names and acronyms correctly capitalized.

**Why:** Sentence case makes field labels easier to scan and keeps the form consistent.

**Exceptions:** Preserve capitalization in product names and acronyms, such as “API key” and “Azure Blob Storage.”

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      account_name:
        type: string
        title: Account Name
        description: Name to assign to the account created by this connector.
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    properties:
      account_name:
        type: string
        title: Account name
        description: Name to assign to the account created by this connector.
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
access_token: Optional[str] = Field(
    title="Access Token",
    description="Generate a Meta system user access token in Meta Business Settings > Users > System users.",
    airbyte_secret=True,
)
```

```python title="Good"
access_token: Optional[str] = Field(
    title="Access token",
    description="Generate a Meta system user access token in Meta Business Settings > Users > System users.",
    airbyte_secret=True,
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```json title="Poor"
{
  "required": ["ca_certificate"],
  "properties": {
    "ca_certificate": {
      "type": "string",
      "title": "CA Certificate",
      "description": "Certificate used to verify the database server's TLS identity. Obtain it from your database provider's SSL/TLS settings.",
      "airbyte_secret": true
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("ca_certificate")
@JsonSchemaTitle("CA certificate")
@JsonPropertyDescription("Certificate used to verify the database server's TLS identity. Obtain it from your database provider's SSL/TLS settings.")
@JsonSchemaInject(json = """{"airbyte_secret":true}""")
lateinit var sslCertificate: String
```

```json title="Good: spec.json"
{
  "required": ["ca_certificate"],
  "properties": {
    "ca_certificate": {
      "type": "string",
      "title": "CA certificate",
      "description": "Certificate used to verify the database server's TLS identity. Obtain it from your database provider's SSL/TLS settings.",
      "airbyte_secret": true
    }
  }
}
```

</TabItem>
</Tabs>

### UX-03: Description says more than the title {#ux-03}

**Rule:** Explain the field's purpose in its description instead of repeating its title. Add context that helps the user choose a value.

**Why:** A description that repeats the label does not help users decide what to enter.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        type: integer
        title: Lookback window
        description: Lookback window in days.
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        type: integer
        title: Lookback window
        description: Also known as the attribution or conversion window, this sets how many days of past records the connector revisits. A larger window can capture late-arriving updates but increases the records processed.
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
lookback_window: Optional[PositiveInt] = Field(
    title="Lookback window",
    description="Lookback window",
)
```

```python title="Good"
client_secret: str = Field(
    title="Client secret",
    description="Secret used to authenticate the Facebook Marketing app. Find it in Meta for Developers under your app's Basic settings.",
    airbyte_secret=True,
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```kotlin title="Poor: Kotlin"
@JsonProperty("project_id")
@JsonSchemaTitle("Project ID")
@JsonPropertyDescription("Project ID.")
lateinit var projectId: String
```

```json title="Poor: spec.json"
{
  "required": ["project_id"],
  "properties": {
    "project_id": {
      "type": "string",
      "title": "Project ID",
      "description": "Project ID."
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("project_id")
@JsonSchemaTitle("Project ID")
@JsonPropertyDescription("Google Cloud project ID containing the BigQuery datasets to read. Find it in Google Cloud Console, then follow the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#setup-the-bigquery-source-in-airbyte\">BigQuery setup guide</a>.")
lateinit var projectId: String
```

```json title="Good: spec.json"
{
  "required": ["project_id"],
  "properties": {
    "project_id": {
      "type": "string",
      "title": "Project ID",
      "description": "Google Cloud project ID containing the BigQuery datasets to read. Find it in Google Cloud Console, then follow the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#setup-the-bigquery-source-in-airbyte\">BigQuery setup guide</a>."
    }
  }
}
```

</TabItem>
</Tabs>

### UX-04: Required fields have a default when a safe value exists {#ux-04}

**Rule:** Give required fields a default when a safe value exists. A common region or `is_sandbox: false` can be a safe default; never default credentials or IDs.

**Why:** A safe default pre-fills the form and saves users from choosing a value that works for most configurations.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    required: [aws_region_name]
    properties:
      aws_region_name:
        type: string
        title: AWS region
        description: AWS region in which CloudTrail stores trail events. Choose the region used by your trail in the AWS console.
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    required: [aws_region_name]
    properties:
      aws_region_name:
        type: string
        title: AWS region
        description: AWS region in which CloudTrail stores trail events. Choose the region used by your trail in the AWS console.
        default: us-east-1
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
aws_region_name: str = Field(
    ...,
    title="AWS region",
    description="AWS region in which CloudTrail stores trail events.",
)
```

```json title="Good"
{
  "required": ["format"],
  "properties": {
    "format": {
      "type": "string",
      "enum": ["csv", "json"],
      "default": "csv",
      "title": "File format",
      "description": "Format used to parse each source file. Choose a value that matches the file's encoding."
    }
  }
}
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```json title="Poor"
{
  "required": ["aws_region_name"],
  "properties": {
    "aws_region_name": {
      "type": "string",
      "title": "AWS region",
      "description": "AWS region in which CloudTrail stores trail events. Choose the region used by your trail in the AWS console."
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("aws_region_name")
@JsonSchemaTitle("AWS region")
@JsonPropertyDescription("AWS region in which CloudTrail stores trail events. Choose the region used by your trail in the AWS console.")
@JsonSchemaInject(json = """{"default":"us-east-1"}""")
var awsRegionName: String = "us-east-1"
```

```json title="Good: spec.json"
{
  "required": ["aws_region_name"],
  "properties": {
    "aws_region_name": {
      "type": "string",
      "title": "AWS region",
      "description": "AWS region in which CloudTrail stores trail events. Choose the region used by your trail in the AWS console.",
      "default": "us-east-1"
    }
  }
}
```

</TabItem>
</Tabs>

### UX-05: `pattern` has a readable `pattern_descriptor` {#ux-05}

**Rule:** When you validate a value with `pattern`, provide a readable `pattern_descriptor`. Describe the expected format rather than relying on users to interpret a regular expression.

**Why:** The form shows a readable hint beside the field when `pattern_descriptor` is set or the web application recognizes the pattern. An explicit descriptor keeps other patterns understandable.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      account_identifier:
        type: string
        title: Account identifier
        description: Account identifier used to select the account to replicate. Find it in the account settings page.
        pattern: "^[A-Z]{3}-[0-9]{4}$"
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    properties:
      account_identifier:
        type: string
        title: Account identifier
        description: Account identifier used to select the account to replicate. Find it in the account settings page.
        pattern: "^[A-Z]{3}-[0-9]{4}$"
        pattern_descriptor: Enter three uppercase letters, a hyphen, and four digits.
```

</TabItem>
<TabItem value="python" label="Python">

```json title="Poor"
{
  "properties": {
    "customer_id": {
      "type": "string",
      "title": "Customer ID(s)",
      "description": "Comma-separated list of 10-digit customer IDs without dashes. Find these IDs in the Google Ads account using the <a href=\"https://docs.airbyte.com/integrations/sources/google-ads#setup-guide\">setup guide</a>.",
      "pattern": "^[0-9]{10}(,[0-9]{10})*$"
    }
  }
}
```

```json title="Good"
{
  "properties": {
    "customer_id": {
      "type": "string",
      "title": "Customer ID(s)",
      "description": "Comma-separated list of 10-digit customer IDs without dashes. Find these IDs in the Google Ads account using the <a href=\"https://docs.airbyte.com/integrations/sources/google-ads#setup-guide\">setup guide</a>.",
      "pattern": "^[0-9]{10}(,[0-9]{10})*$",
      "pattern_descriptor": "The customer ID must be 10 digits. Separate multiple customer IDs using commas.",
      "examples": ["6783948572,5839201945"]
    }
  }
}
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```kotlin title="Poor: Kotlin"
@JsonProperty("cluster_name")
@JsonSchemaTitle("Cluster name")
@JsonPropertyDescription("Name of the ClickHouse cluster configured for this destination. Find it in the ClickHouse Cloud service details.")
@JsonSchemaInject(json = """{"pattern":"^[A-Za-z0-9_.-]*$"}""")
lateinit var clusterName: String
```

```json title="Poor: spec.json"
{
  "required": ["cluster_name"],
  "properties": {
    "cluster_name": {
      "type": "string",
      "title": "Cluster name",
      "description": "Name of the ClickHouse cluster configured for this destination. Find it in the ClickHouse Cloud service details.",
      "pattern": "^[A-Za-z0-9_.-]*$"
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("cluster_name")
@JsonSchemaTitle("Cluster name")
@JsonPropertyDescription("Name of the ClickHouse cluster configured for this destination. Find it in the ClickHouse Cloud service details.")
@JsonSchemaInject(json = """{"pattern":"^[A-Za-z0-9_.-]*$","pattern_descriptor":"Use letters, numbers, periods, underscores, or hyphens."}""")
lateinit var clusterName: String
```

```json title="Good: spec.json"
{
  "required": ["cluster_name"],
  "properties": {
    "cluster_name": {
      "type": "string",
      "title": "Cluster name",
      "description": "Name of the ClickHouse cluster configured for this destination. Find it in the ClickHouse Cloud service details.",
      "pattern": "^[A-Za-z0-9_.-]*$",
      "pattern_descriptor": "Use letters, numbers, periods, underscores, or hyphens."
    }
  }
}
```

</TabItem>
</Tabs>

### UX-06: Secrets marked `airbyte_secret` {#ux-06}

**Rule:** Mark every secret field with `airbyte_secret: true`. Do not mark public values, IDs, or other non-secret fields as secrets.

**Why:** Unmarked credentials appear in a regular text control instead of a masked secret control.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    required: [aws_secret_key]
    properties:
      aws_secret_key:
        type: string
        title: AWS secret access key
        description: Used to sign CloudTrail API requests. Create an access key for the connector's IAM user in AWS IAM.
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    required: [aws_secret_key]
    properties:
      aws_secret_key:
        type: string
        title: AWS secret access key
        description: Used to sign CloudTrail API requests. Create an access key for the connector's IAM user in AWS IAM.
        airbyte_secret: true
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
client_secret: str = Field(
    title="Client secret",
    description="Secret used to authenticate the Facebook Marketing app. Find it in Meta for Developers under your app's Basic settings.",
)
```

```python title="Good"
client_secret: str = Field(
    title="Client secret",
    description="Secret used to authenticate the Facebook Marketing app. Find it in Meta for Developers under your app's Basic settings.",
    airbyte_secret=True,
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```kotlin title="Poor: Kotlin"
@JsonProperty("password")
@JsonSchemaTitle("Password")
@JsonPropertyDescription("Password associated with the MySQL username. Use the value configured for that account in the database.")
lateinit var password: String
```

```json title="Poor: spec.json"
{
  "required": ["password"],
  "properties": {
    "password": {
      "type": "string",
      "title": "Password",
      "description": "Password associated with the MySQL username. Use the value configured for that account in the database."
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("password")
@JsonSchemaTitle("Password")
@JsonPropertyDescription("Password associated with the MySQL username. Use the value configured for that account in the database.")
@JsonSchemaInject(json = """{"airbyte_secret":true}""")
lateinit var password: String
```

```json title="Good: spec.json"
{
  "required": ["password"],
  "properties": {
    "password": {
      "type": "string",
      "title": "Password",
      "description": "Password associated with the MySQL username. Use the value configured for that account in the database.",
      "airbyte_secret": true
    }
  }
}
```

</TabItem>
</Tabs>

### UX-07: Fields with a default are required {#ux-07}

**Rule:** If a field has a default, add it to the parent's list of required properties. This ensures every saved configuration contains the value that determines the connector's behavior.

**Why:** The web app fills defaults only when someone creates a configuration in the UI. API, Terraform, and PyAirbyte callers do not get those defaults, so an optional field with a default may be missing from saved configurations.

:::note Coming soon
Do not move existing optional fields with defaults into `required` yet. Today, required fields always show in the main form. Making an existing field required is a breaking change because API and Terraform updates of saved configurations that lack the field fail validation.
:::

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      num_workers:
        type: integer
        title: Worker count
        description: Number of workers used to process the replication job; larger counts can process data faster but use more resources.
        default: 2
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    required: [aws_region_name]
    properties:
      aws_region_name:
        type: string
        title: AWS region
        description: AWS region in which CloudTrail stores trail events. Choose the region used by your trail in the AWS console.
        default: us-east-1
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
time_increment: Optional[PositiveInt] = Field(
    default=1,
    title="Time increment",
    description="Number of days used to aggregate statistics for custom insights; larger values yield wider reporting periods.",
    minimum=1,
    maximum=89,
)
```

```json title="Good"
{
  "required": ["format"],
  "properties": {
    "format": {
      "type": "string",
      "enum": ["csv", "json"],
      "default": "csv",
      "title": "File format",
      "description": "Format used to parse each source file. Choose a value that matches the file's encoding."
    }
  }
}
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```kotlin title="Poor: Kotlin"
@JsonProperty("discover_timeout_seconds")
@JsonSchemaTitle("Discovery timeout")
@JsonPropertyDescription("Number of seconds to wait for the connector to discover available schemas.")
@JsonSchemaInject(json = """{"default":600}""")
var discoverTimeoutSeconds: Int? = 600
```

```json title="Poor: spec.json"
{
  "properties": {
    "discover_timeout_seconds": {
      "type": "integer",
      "title": "Discovery timeout",
      "description": "Number of seconds to wait for the connector to discover available schemas.",
      "default": 600
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("schema")
@JsonSchemaTitle("Schema name")
@JsonPropertyDescription("Name of the SQL Server schema where the destination creates tables. The public schema is a common default when no custom schema is needed.")
@JsonSchemaInject(json = """{"default":"public"}""")
var schema: String = "public"
```

```json title="Good: spec.json"
{
  "required": ["schema"],
  "properties": {
    "schema": {
      "type": "string",
      "title": "Schema name",
      "description": "Name of the SQL Server schema where the destination creates tables. The public schema is a common default when no custom schema is needed.",
      "default": "public"
    }
  }
}
```

</TabItem>
</Tabs>

### UX-08: Explain meaning and impact {#ux-08}

**Rule:** Explain what a field controls and how changing it affects the data, sync, or output. Give users enough context to choose a value.

**Why:** A vague label or short description leaves users guessing about the effect of a setting.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        type: integer
        title: Lookback window
        description: Number of days before the cursor to check for records.
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    properties:
      lookback_window:
        type: integer
        title: Lookback window
        description: Number of days before the cursor to revisit during incremental sync. A larger window can capture late-arriving updates but increases the records and API requests processed.
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
lookback_window: Optional[PositiveInt] = Field(
    title="Lookback window",
    description="Number of days before the cursor to check for records.",
)
```

```python title="Good"
insights_lookback_window: Optional[PositiveInt] = Field(
    title="Insights lookback window",
    maximum=28,
    minimum=1,
    description=(
        "The attribution period to refresh for custom insights. A larger value includes older "
        "insights that may have changed and can increase the amount of data requested."
    ),
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```kotlin title="Poor: Kotlin"
@JsonProperty("connection_timeout_seconds")
@JsonSchemaTitle("Connection timeout")
@JsonPropertyDescription("Timeout in seconds for connection requests.")
var connectionTimeoutSeconds: Int? = null
```

```json title="Poor: spec.json"
{
  "properties": {
    "connection_timeout_seconds": {
      "type": "integer",
      "title": "Connection timeout",
      "description": "Timeout in seconds for connection requests."
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("credentials_json")
@JsonSchemaTitle("Service account key JSON")
@JsonPropertyDescription("JSON key for the service account that lets the connector authenticate to BigQuery. Without a valid key, the connector cannot read the dataset. Create and download it using the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">service account key instructions</a>.")
@JsonSchemaInject(json = """{"airbyte_secret":true}""")
lateinit var credentialsJson: String
```

```json title="Good: spec.json"
{
  "required": ["credentials_json"],
  "properties": {
    "credentials_json": {
      "type": "string",
      "title": "Service account key JSON",
      "description": "JSON key for the service account that lets the connector authenticate to BigQuery. Without a valid key, the connector cannot read the dataset. Create and download it using the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">service account key instructions</a>.",
      "airbyte_secret": true
    }
  }
}
```

</TabItem>
</Tabs>

### UX-09: Say where to get each value {#ux-09}

**Rule:** Tell users where to find each value they must provide. Link to setup instructions when they can explain the steps.

**Why:** Users should not have to search a vendor's site or guess which credential or identifier you need.

**Exceptions:** Do not apply this rule to fields OAuth fills in through `advanced_auth.complete_oauth_output_specification`.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    required: [access_key]
    properties:
      access_key:
        type: string
        title: Gong access key
        description: Key used to authenticate requests to the Gong API.
        airbyte_secret: true
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    required: [api_key]
    properties:
      api_key:
        type: string
        title: API key
        description: API key for your Amplitude project. Create it in your organization's settings using the <a href="https://docs.airbyte.com/integrations/sources/amplitude#setup-guide">setup guide</a>.
        airbyte_secret: true
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
access_key: str = Field(
    title="Gong access key",
    description="Key used to authenticate requests to the Gong API.",
    airbyte_secret=True,
)
```

```python title="Good"
access_token: Optional[str] = Field(
    title="Access token",
    description="Generate a Meta system user access token in Meta Business Settings > Users > System users > Generate new token for your app.",
    airbyte_secret=True,
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```json title="Poor"
{
  "required": ["credentials_json"],
  "properties": {
    "credentials_json": {
      "type": "string",
      "title": "Service account key JSON",
      "description": "JSON key used to authenticate the BigQuery connection.",
      "airbyte_secret": true
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("credentials_json")
@JsonSchemaTitle("Service account key JSON")
@JsonPropertyDescription("JSON key for the service account that lets the connector authenticate to BigQuery. Create and download it using the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">service account key instructions</a>.")
@JsonSchemaInject(json = """{"airbyte_secret":true}""")
lateinit var credentialsJson: String
```

```json title="Good: spec.json"
{
  "required": ["credentials_json"],
  "properties": {
    "credentials_json": {
      "type": "string",
      "title": "Service account key JSON",
      "description": "JSON key for the service account that lets the connector authenticate to BigQuery. Create and download it using the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">service account key instructions</a>.",
      "airbyte_secret": true
    }
  }
}
```

</TabItem>
</Tabs>

### UX-10: Doc links point to anchors {#ux-10}

**Rule:** Link to the relevant heading or setup section when a page has one. Use a stable, current URL rather than sending users to a page's top-level overview.

**Why:** An anchored link takes users directly to the instructions they need.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    required: [access_token]
    properties:
      access_token:
        type: string
        title: Private app access token
        description: Create a private app in HubSpot and copy its access token. See the <a href="https://docs.airbyte.com/integrations/sources/hubspot">HubSpot setup guide</a>.
        airbyte_secret: true
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    required: [api_key]
    properties:
      api_key:
        type: string
        title: API key
        description: API key for your Amplitude project. Create it in your organization's settings using the <a href="https://docs.airbyte.com/integrations/sources/amplitude#setup-guide">setup guide</a>.
        airbyte_secret: true
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
access_token: str = Field(
    ...,
    title="Access token",
    description="Generate a Meta system user access token in Meta Business Settings > Users > System users. See the <a href=\"https://docs.airbyte.com/integrations/sources/facebook-marketing\">Facebook Marketing setup guide</a>.",
    airbyte_secret=True,
)
```

```json title="Good"
{
  "properties": {
    "customer_id": {
      "type": "string",
      "title": "Customer ID(s)",
      "description": "Comma-separated list of 10-digit customer IDs without dashes. Find these IDs in the Google Ads account using the <a href=\"https://docs.airbyte.com/integrations/sources/google-ads#setup-guide\">setup guide</a>.",
      "pattern": "^[0-9]{10}(,[0-9]{10})*$",
      "pattern_descriptor": "The customer ID must be 10 digits. Separate multiple customer IDs using commas.",
      "examples": ["6783948572,5839201945"]
    }
  }
}
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```json title="Poor"
{
  "required": ["credentials_json"],
  "properties": {
    "credentials_json": {
      "type": "string",
      "title": "Service account key JSON",
      "description": "Create and download the key from Google Cloud Console using the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery\">service account key instructions</a>.",
      "airbyte_secret": true
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("credentials_json")
@JsonSchemaTitle("Service account key JSON")
@JsonPropertyDescription("JSON key for the service account that lets the connector authenticate to BigQuery. Create and download it using the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">service account key instructions</a>.")
@JsonSchemaInject(json = """{"airbyte_secret":true}""")
lateinit var credentialsJson: String
```

```json title="Good: spec.json"
{
  "required": ["credentials_json"],
  "properties": {
    "credentials_json": {
      "type": "string",
      "title": "Service account key JSON",
      "description": "JSON key for the service account that lets the connector authenticate to BigQuery. Create and download it using the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#service-account-key\">service account key instructions</a>.",
      "airbyte_secret": true
    }
  }
}
```

</TabItem>
</Tabs>

### UX-11: Auth is not entirely optional {#ux-11}

**Rule:** Put the method selector (`credentials`) in the top-level `required` list and define one `oneOf` option per authentication method. If anonymous access is supported, represent **No auth** as an explicit option rather than making the selector optional; GitHub, HubSpot, and Jira manifests demonstrate required selectors with method options.

**Why:** If the selector is optional, users can save a configuration without choosing or providing an authentication method.

**Exceptions:** Deliberately optional credentials, such as a public API key or a database password that can be omitted, are still reported. You can ignore the finding when the connector intentionally supports that configuration.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      credentials:
        type: object
        title: Authentication
        description: Choose API key authentication or no authentication.
        oneOf:
          - title: API key
            type: object
            required: [auth_type, api_key]
            properties:
              auth_type:
                type: string
                const: API_KEY
              api_key:
                type: string
                title: API key
                description: Create an API key in the provider's developer console.
                airbyte_secret: true
          - title: No auth
            type: object
            required: [auth_type]
            properties:
              auth_type:
                type: string
                const: NO_AUTH
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    required: [credentials]
    properties:
      credentials:
        type: object
        title: Authentication
        description: Choose API key authentication or no authentication.
        oneOf:
          - title: API key
            type: object
            required: [auth_type, api_key]
            properties:
              auth_type:
                type: string
                const: API_KEY
              api_key:
                type: string
                title: API key
                description: Create an API key in the provider's developer console.
                airbyte_secret: true
          - title: No auth
            type: object
            required: [auth_type]
            properties:
              auth_type:
                type: string
                const: NO_AUTH
```

</TabItem>
<TabItem value="python" label="Python">

```python title="Poor"
credentials: Optional[Union[OAuthCredentials, ServiceAccountCredentials]] = Field(
    title="Authentication",
    description="Credentials for connecting to the Facebook Marketing API.",
    type="object",
)
```

```python title="Good"
credentials: Union[OAuthCredentials, ServiceAccountCredentials] = Field(
    title="Authentication",
    description="Credentials for connecting to the Facebook Marketing API",
    type="object",
)
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```json title="Poor"
{
  "properties": {
    "credentials": {
      "type": "object",
      "title": "Authentication",
      "description": "Choose API key authentication or no authentication.",
      "oneOf": [
        {
          "title": "API key",
          "type": "object",
          "required": ["auth_type", "api_key"],
          "properties": {
            "auth_type": {"type": "string", "const": "API_KEY"},
            "api_key": {
              "type": "string",
              "title": "API key",
              "description": "Create an API key in the provider's developer console.",
              "airbyte_secret": true
            }
          }
        },
        {
          "title": "No auth",
          "type": "object",
          "required": ["auth_type"],
          "properties": {
            "auth_type": {"type": "string", "const": "NO_AUTH"}
          }
        }
      ]
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "auth_type")
@JsonSubTypes(
    JsonSubTypes.Type(value = ApiKeyCredentials::class, name = "API_KEY"),
    JsonSubTypes.Type(value = NoAuthCredentials::class, name = "NO_AUTH"),
)
@JsonSchemaTitle("Authentication")
@JsonSchemaDescription("Choose API key authentication or no authentication.")
sealed interface Credentials

@JsonSchemaTitle("API key")
class ApiKeyCredentials : Credentials {
    @JsonProperty("api_key", required = true)
    @JsonSchemaTitle("API key")
    @JsonPropertyDescription("Create an API key in the provider's developer console.")
    @JsonSchemaInject(json = """{"airbyte_secret":true}""")
    lateinit var apiKey: String
}

@JsonSchemaTitle("No auth")
class NoAuthCredentials : Credentials

class SourceSpec {
    @JsonProperty("credentials", required = true)
    @JsonSchemaTitle("Authentication")
    @JsonPropertyDescription("Choose API key authentication or no authentication.")
    lateinit var credentials: Credentials
}
```

```json title="Good: spec.json"
{
  "required": ["credentials"],
  "properties": {
    "credentials": {
      "type": "object",
      "title": "Authentication",
      "description": "Choose API key authentication or no authentication.",
      "oneOf": [
        {
          "title": "API key",
          "type": "object",
          "required": ["auth_type", "api_key"],
          "properties": {
            "auth_type": {"type": "string", "const": "API_KEY"},
            "api_key": {
              "type": "string",
              "title": "API key",
              "description": "Create an API key in the provider's developer console.",
              "airbyte_secret": true
            }
          }
        },
        {
          "title": "No auth",
          "type": "object",
          "required": ["auth_type"],
          "properties": {
            "auth_type": {"type": "string", "const": "NO_AUTH"}
          }
        }
      ]
    }
  }
}
```

</TabItem>
</Tabs>

### UX-12: Date pattern also sets `format: date`/`date-time` {#ux-12}

**Rule:** For a date or date-time field, set `type: string`, the matching `format`, and a `pattern` with a readable `pattern_descriptor`. Use `date` for a date and `date-time` when the value includes a time.

**Why:** The date picker requires the string type and date format. A pattern without a format renders a plain text field.

<Tabs groupId="cdk">
<TabItem value="yaml" label="YAML">

```yaml title="Poor"
spec:
  connection_specification:
    type: object
    properties:
      start_date:
        type: string
        title: Start date
        description: Date from which to start syncing records; earlier records are not replicated.
        pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
        pattern_descriptor: YYYY-MM-DD
```

```yaml title="Good"
spec:
  connection_specification:
    type: object
    properties:
      start_date:
        type: string
        title: Start date
        description: UTC date from which to start syncing Google Ads records; earlier records are not replicated.
        format: date
        pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
        pattern_descriptor: YYYY-MM-DD
```

</TabItem>
<TabItem value="python" label="Python">

```json title="Poor"
{
  "properties": {
    "start_date": {
      "type": "string",
      "title": "Start date",
      "description": "UTC date from which to start syncing Google Ads records; earlier records are not replicated.",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
      "pattern_descriptor": "YYYY-MM-DD"
    }
  }
}
```

```json title="Good"
{
  "properties": {
    "start_date": {
      "type": "string",
      "title": "Start date",
      "description": "UTC date from which to start syncing Google Ads records; earlier records are not replicated.",
      "format": "date",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
      "pattern_descriptor": "YYYY-MM-DD",
      "examples": ["2017-01-25"]
    }
  }
}
```

</TabItem>
<TabItem value="java" label="Java/Kotlin">

```json title="Poor"
{
  "required": ["start_date"],
  "properties": {
    "start_date": {
      "type": "string",
      "title": "Start date",
      "description": "Date from which to start syncing records; earlier records are not replicated.",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
      "pattern_descriptor": "YYYY-MM-DD"
    }
  }
}
```

```kotlin title="Good: Kotlin"
@JsonProperty("start_date")
@JsonSchemaTitle("Start date")
@JsonPropertyDescription("Date from which to start syncing records; earlier records are not replicated.")
@JsonSchemaInject(json = """{"format":"date","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}$","pattern_descriptor":"YYYY-MM-DD"}""")
lateinit var startDate: String

@JsonProperty("created_at")
@JsonSchemaTitle("Creation timestamp")
@JsonPropertyDescription("Timestamp when the record was created, including its time and UTC timezone.")
@JsonSchemaInject(json = """{"format":"date-time","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$","pattern_descriptor":"YYYY-MM-DDTHH:mm:ssZ"}""")
lateinit var createdAt: String
```

```json title="Good: spec.json"
{
  "required": ["start_date", "created_at"],
  "properties": {
    "start_date": {
      "type": "string",
      "title": "Start date",
      "description": "Date from which to start syncing records; earlier records are not replicated.",
      "format": "date",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
      "pattern_descriptor": "YYYY-MM-DD"
    },
    "created_at": {
      "type": "string",
      "title": "Creation timestamp",
      "description": "Timestamp when the record was created, including its time and UTC timezone.",
      "format": "date-time",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
      "pattern_descriptor": "YYYY-MM-DDTHH:mm:ssZ"
    }
  }
}
```

</TabItem>
</Tabs>

## Other form guidance

Configuration adds work and creates opportunities for confusion. Avoid asking users to configure a behavior when the connector can choose a safe value or handle it automatically. Avoid exposing implementation details such as retry counts unless users need them to reach a goal.

Use `order` and `group` to arrange related fields. Keep technical or niche options out of the main flow with collapsed groups, and use `always_show` only when users need to see an optional field immediately. Give every `oneOf` option a `title`, add useful `examples`, and use `enum` instead of free text when the accepted values are fixed.

Fail fast and provide an actionable error. Use `pattern` to reject malformed values and `pattern_descriptor` to explain the expected format. See [UX-05](#ux-05) and [UX-12](#ux-12).

## Output data and schemas

### Strongly favor ELT over ETL

Extract-load-transform (ELT) means a connector loads data into the destination in the shape the source provides it, and users transform it afterward. Extract-transform-load (ETL) means the connector reshapes data before loading it.

A connector's features shouldn't stand between users and their goals. When a connector honors the most literal representation of the source API and leaves transformation to the user's warehouse, every user gets a faithful copy of their data and full control over its final shape. ELT is the most democratic model Airbyte can offer, for the following reasons.

#### Removes Airbyte as a bottleneck

If a connector shapes its output for one way of using the data, users who need a different shape must ask for connector changes and wait for them. When the connector loads data the way the source provides it, each user can transform it in their destination, on their own schedule and with their own tools.

#### Will always be backwards compatible

APIs already follow strong conventions to maintain backwards compatibility. By transforming data, we break this guarantee, which means we may break downstream flows for our users.

#### Future proof

We may have a vision of what a user needs today. But if our persona evolves next year, then we’ll probably also need to adapt our transformation logic, which would require significant development and data migration efforts.

#### More flexible

Current users have different needs from data. By being opinionated on how they should consume data, we are effectively favoring one user persona over the other. While there might be some cases where this is warranted, it should be done with extreme intentionality.

#### More efficient

With ETL, if the “T” ever needs to change, then we need to re-extract all data for all users. This is computationally and financially expensive and will place a lot of pressure on the source systems as we re-extract all data.

### Describe output schemas as completely and reliably as possible

Our most popular destinations use strongly typed systems such as Postgres and BigQuery, and file formats such as Parquet.

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

For example, to set up CDC for databases, a user must create logical replication slots and do a few other things. These steps should be documented with examples or screenshots wherever possible (for example, the SQL statements to run, the required permissions, and the relevant screen).

## External documentation

Write external-facing connector documentation on [docs.airbyte.com](https://docs.airbyte.com), such as the [Amazon Seller Partner page](https://docs.airbyte.com/integrations/sources/amazon-seller-partner).

### Documentation should communicate persona-impacting behaviors

When writing documentation ask: who is the intended target persona for a piece of documentation, and what information do they need to understand how this connector impacts their workflows?

For example, data analysts and analytics engineers probably do not care which implementation we use for database replication. To them, the important thing is that we provide Change Data Capture (CDC). The implementation is a detail. Therefore, when communicating information about database replication, we should emphasize the end behaviors rather than implementation details.

**Example**: Don’t say: “The CDC implementation cannot process UTF-16 characters.”

Instead, say: “When using CDC, UTF-16 characters are not currently supported.”

A user who does not know which implementation we use might be confused by the first phrasing, so we should use the second phrasing.
