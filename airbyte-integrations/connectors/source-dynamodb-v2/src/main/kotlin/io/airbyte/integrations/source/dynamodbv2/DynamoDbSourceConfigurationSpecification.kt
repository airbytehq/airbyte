/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

/**
 * The object which is mapped to the DynamoDB source configuration JSON.
 *
 * Property names are those of the legacy `source-dynamodb` connector (`credentials` with
 * `auth_type: "User"`, `access_key_id`, `secret_access_key`, `endpoint`, `region`,
 * `reserved_attribute_names`, `ignore_missing_read_permissions_tables`), so a legacy access-key
 * configuration still loads. Unlike the legacy spec, credentials can only come from this
 * configuration: the connector runs in a container with no AWS profile, instance role or
 * environment credentials, so the legacy "Role Based Authentication" option (SDK default
 * credentials chain) is gone, `region` is required, and temporary credentials / IAM role assumption
 * are supported. Use [DynamoDbSourceConfiguration] instead wherever possible.
 */
@JsonSchemaTitle("DynamoDB Source Spec")
@JsonPropertyOrder(
    value =
        [
            "credentials",
            "region",
            "endpoint",
            "reserved_attribute_names",
            "ignore_missing_read_permissions_tables",
            "discover_sample_size",
        ],
)
@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class DynamoDbSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("credentials")
    @JsonSchemaTitle("Credentials")
    @JsonSchemaDescription(
        "How the connector authenticates with AWS. Credentials are read from this configuration only; the connector cannot use AWS profiles, instance roles or environment variables.",
    )
    @JsonSchemaInject(json = """{"order":0,"display_type":"dropdown"}""")
    lateinit var credentials: CredentialsSpecification

    /** Null when the (required) `credentials` property is absent from the config JSON. */
    fun credentialsOrNull(): CredentialsSpecification? =
        if (this::credentials.isInitialized) credentials else null

    @JsonProperty("region")
    @JsonSchemaTitle("AWS Region")
    @JsonSchemaDescription("The AWS region of the DynamoDB tables.")
    @JsonSchemaInject(
        json =
            """{"order":1,"examples":["us-east-1"],"enum":["af-south-1","ap-east-1","ap-east-2","ap-northeast-1","ap-northeast-2","ap-northeast-3","ap-south-1","ap-south-2","ap-southeast-1","ap-southeast-2","ap-southeast-3","ap-southeast-4","ap-southeast-5","ap-southeast-6","ap-southeast-7","ca-central-1","ca-west-1","cn-north-1","cn-northwest-1","eu-central-1","eu-central-2","eu-north-1","eu-south-1","eu-south-2","eu-west-1","eu-west-2","eu-west-3","eusc-de-east-1","il-central-1","me-central-1","me-south-1","mx-central-1","sa-east-1","us-east-1","us-east-2","us-gov-east-1","us-gov-west-1","us-west-1","us-west-2"]}""",
    )
    lateinit var region: String

    /** Null when the (required) `region` property is absent from the config JSON. */
    fun regionOrNull(): String? = if (this::region.isInitialized) region else null

    @JsonProperty("endpoint")
    @JsonSchemaTitle("DynamoDB Endpoint")
    @JsonSchemaDescription(
        "Optional endpoint override, for example a VPC endpoint, a FIPS endpoint or a DynamoDB Local instance. Leave empty to use the public endpoint of the region.",
    )
    @JsonSchemaInject(
        json =
            """{"order":2,"examples":["https://dynamodb-fips.us-east-1.amazonaws.com","http://localhost:8000"]}""",
    )
    var endpoint: String? = null

    @JsonProperty("reserved_attribute_names")
    @JsonSchemaTitle("Reserved attribute names")
    @JsonSchemaDescription(
        "Comma separated names of attributes that are DynamoDB reserved words or contain special characters. No longer needed: every attribute is now aliased in scan expressions; kept for backward compatibility.",
    )
    @JsonSchemaInject(json = """{"order":3,"examples":["name, field_name, field-name"]}""")
    var reservedAttributeNames: String? = null

    @JsonProperty("ignore_missing_read_permissions_tables")
    @JsonSchemaTitle("Ignore missing read permissions tables")
    @JsonSchemaDescription("Ignore tables with missing scan/read permissions")
    @JsonSchemaInject(json = """{"order":4,"default":false}""")
    var ignoreMissingReadPermissionsTables: Boolean? = null

    @JsonProperty("discover_sample_size")
    @JsonSchemaTitle("Discovery sample size (Advanced)")
    @JsonSchemaDescription(
        "The maximum number of items to scan per table when discovering its attributes and their types. A larger sample finds rarer attributes but consumes more read capacity. Defaults to 1000.",
    )
    @JsonSchemaInject(
        json =
            """{"order":5,"default":1000,"minimum":1,"maximum":100000,"examples":[1000, 10000]}""",
    )
    var discoverSampleSize: Int? = null

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval (Advanced)")
    @JsonSchemaDescription(
        "How often (in seconds) a stream should checkpoint its progress, when possible. A table is scanned in rounds of about this duration and its state is saved after each round, so that an interrupted sync resumes where it stopped. Defaults to 300.",
    )
    @JsonSchemaInject(
        json = """{"order":6,"default":300,"minimum":1,"examples":[300, 900]}""",
    )
    var checkpointTargetIntervalSeconds: Int? = null

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Concurrency")
    @JsonSchemaInject(json = """{"order":7}""")
    @JsonPropertyDescription(
        "Maximum number of tables scanned at the same time (concurrent Scan requests). Defaults to 1; every table draws on its own read capacity, so a higher value speeds up syncs of many tables.",
    )
    var concurrency: Int? = null

    companion object {
        /** What the legacy connector always sampled. */
        const val DEFAULT_DISCOVER_SAMPLE_SIZE = 1000
        const val MIN_DISCOVER_SAMPLE_SIZE = 1
        const val MAX_DISCOVER_SAMPLE_SIZE = 100_000

        /** Same default as the Bulk CDK JDBC sources. */
        const val DEFAULT_CHECKPOINT_TARGET_INTERVAL_SECONDS = 300
    }
}

/**
 * The `credentials` oneOf. `auth_type: "User"` is the legacy discriminator value for access keys
 * and is kept so that legacy configurations load unchanged.
 */
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    property = CredentialsSpecification.AUTH_TYPE,
    // Any other `auth_type`, notably the legacy "Role", deserializes to this marker so that the
    // configuration factory can reject it with a clear message. Not part of the generated spec.
    defaultImpl = UnsupportedCredentialsSpecification::class,
)
@JsonSubTypes(
    JsonSubTypes.Type(value = AccessKeyCredentialsSpecification::class, name = "User"),
    JsonSubTypes.Type(value = AssumeRoleCredentialsSpecification::class, name = "AssumeRole"),
)
sealed interface CredentialsSpecification {
    val accessKeyId: String
    val secretAccessKey: String
    val sessionToken: String?

    companion object {
        const val AUTH_TYPE = "auth_type"
    }
}

/** An IAM user's access key, or temporary credentials (access key + session token) from STS. */
@JsonSchemaTitle("Access Key")
@JsonSchemaDescription(
    "Authenticate with the access key of an IAM user, or with temporary credentials (access key, secret access key and session token) issued by AWS STS.",
)
@JsonPropertyOrder(value = ["access_key_id", "secret_access_key", "session_token"])
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class AccessKeyCredentialsSpecification : CredentialsSpecification {
    @JsonProperty("access_key_id")
    @JsonSchemaTitle("Access Key ID")
    @JsonSchemaDescription(
        "The access key ID. Airbyte needs the dynamodb:ListTables, dynamodb:DescribeTable and dynamodb:Scan permissions on the tables to replicate.",
    )
    @JsonSchemaInject(
        json = """{"order":1,"airbyte_secret":true,"examples":["A012345678910EXAMPLE"]}""",
    )
    override lateinit var accessKeyId: String

    @JsonProperty("secret_access_key")
    @JsonSchemaTitle("Secret Access Key")
    @JsonSchemaDescription("The secret access key that corresponds to the access key ID.")
    @JsonSchemaInject(
        json =
            """{"order":2,"airbyte_secret":true,"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"]}""",
    )
    override lateinit var secretAccessKey: String

    @JsonProperty("session_token")
    @JsonSchemaTitle("Session Token")
    @JsonSchemaDescription(
        "The session token of temporary credentials issued by AWS STS. Leave empty when using the long-lived access key of an IAM user.",
    )
    @JsonSchemaInject(json = """{"order":3,"airbyte_secret":true}""")
    override var sessionToken: String? = null
}

/**
 * An access key that is allowed to call `sts:AssumeRole` on an IAM role; DynamoDB is then read with
 * the role's temporary credentials (cross-account access, least-privilege roles).
 */
@JsonSchemaTitle("Access Key and IAM Role")
@JsonSchemaDescription(
    "Authenticate with an access key that may assume an IAM role (sts:AssumeRole), then read DynamoDB with the role's temporary credentials. Use this for cross-account access.",
)
@JsonPropertyOrder(
    value = ["access_key_id", "secret_access_key", "session_token", "role_arn", "external_id"]
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class AssumeRoleCredentialsSpecification : CredentialsSpecification {
    @JsonProperty("access_key_id")
    @JsonSchemaTitle("Access Key ID")
    @JsonSchemaDescription(
        "The access key ID of the IAM identity that is allowed to assume the role (sts:AssumeRole).",
    )
    @JsonSchemaInject(
        json = """{"order":1,"airbyte_secret":true,"examples":["A012345678910EXAMPLE"]}""",
    )
    override lateinit var accessKeyId: String

    @JsonProperty("secret_access_key")
    @JsonSchemaTitle("Secret Access Key")
    @JsonSchemaDescription("The secret access key that corresponds to the access key ID.")
    @JsonSchemaInject(
        json =
            """{"order":2,"airbyte_secret":true,"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"]}""",
    )
    override lateinit var secretAccessKey: String

    @JsonProperty("session_token")
    @JsonSchemaTitle("Session Token")
    @JsonSchemaDescription(
        "The session token, only when the access key above is itself a temporary credential issued by AWS STS.",
    )
    @JsonSchemaInject(json = """{"order":3,"airbyte_secret":true}""")
    override var sessionToken: String? = null

    @JsonProperty("role_arn")
    @JsonSchemaTitle("Role ARN")
    @JsonSchemaDescription(
        "The ARN of the IAM role to assume. The role needs the dynamodb:ListTables, dynamodb:DescribeTable and dynamodb:Scan permissions on the tables to replicate, and its trust policy must allow the access key's identity to assume it.",
    )
    @JsonSchemaInject(
        json =
            """{"order":4,"examples":["arn:aws:iam::123456789012:role/airbyte-dynamodb-reader"]}""",
    )
    lateinit var roleArn: String

    @JsonProperty("external_id")
    @JsonSchemaTitle("External ID")
    @JsonSchemaDescription(
        "The external ID that the role's trust policy requires (sts:ExternalId condition), if any.",
    )
    @JsonSchemaInject(json = """{"order":5}""")
    var externalId: String? = null
}

/**
 * Marker for an `auth_type` this connector does not support, for example the legacy `Role` (SDK
 * default credentials chain). Never advertised in the spec; rejected by the configuration factory.
 */
class UnsupportedCredentialsSpecification : CredentialsSpecification {
    override val accessKeyId: String
        get() = ""

    override val secretAccessKey: String
        get() = ""

    override val sessionToken: String?
        get() = null
}
