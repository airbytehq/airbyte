/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.annotation.JsonProperty
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
 * Property names, titles, descriptions, defaults and ordering deliberately mirror the legacy
 * `source-dynamodb` `spec.json`, so that saved configurations keep deserializing and the `spec`
 * output stays identical. Use [DynamoDbSourceConfiguration] instead wherever possible.
 */
@JsonSchemaTitle("Dynamodb Source Spec")
@JsonPropertyOrder(
    value =
        [
            "credentials",
            "endpoint",
            "region",
            "reserved_attribute_names",
            "ignore_missing_read_permissions_tables",
        ],
)
@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class DynamoDbSourceConfigurationSpecification : ConfigurationSpecification() {

    /**
     * Nullable so that it is not part of the schema's `required` list (the legacy spec declares no
     * required property); [DynamoDbSourceConfigurationFactory] rejects a configuration without it.
     */
    @JsonProperty("credentials")
    @JsonSchemaTitle("Credentials")
    @JsonSchemaDescription("Credentials for the service")
    @JsonSchemaInject(json = """{"order":0}""")
    var credentials: CredentialsSpecification? = null

    @JsonProperty("endpoint")
    @JsonSchemaTitle("Dynamodb Endpoint")
    @JsonSchemaDescription("the URL of the Dynamodb database")
    @JsonSchemaInject(json = """{"default":"","examples":["https://{aws_dynamo_db_url}.com"]}""")
    var endpoint: String? = null

    @JsonProperty("region")
    @JsonSchemaTitle("Dynamodb Region")
    @JsonSchemaDescription("The region of the Dynamodb database")
    @JsonSchemaInject(
        json =
            """{"default":"","enum":["","af-south-1","ap-east-1","ap-northeast-1","ap-northeast-2","ap-northeast-3","ap-south-1","ap-south-2","ap-southeast-1","ap-southeast-2","ap-southeast-3","ap-southeast-4","ca-central-1","ca-west-1","cn-north-1","cn-northwest-1","eu-central-1","eu-central-2","eu-north-1","eu-south-1","eu-south-2","eu-west-1","eu-west-2","eu-west-3","il-central-1","me-central-1","me-south-1","sa-east-1","us-east-1","us-east-2","us-gov-east-1","us-gov-west-1","us-west-1","us-west-2"]}""",
    )
    var region: String? = null

    /** `airbyte_secret` is a legacy quirk, kept for spec parity. */
    @JsonProperty("reserved_attribute_names")
    @JsonSchemaTitle("Reserved attribute names")
    @JsonSchemaDescription("Comma separated reserved attribute names present in your tables")
    @JsonSchemaInject(
        json = """{"airbyte_secret":true,"examples":["name, field_name, field-name"]}""",
    )
    var reservedAttributeNames: String? = null

    @JsonProperty("ignore_missing_read_permissions_tables")
    @JsonSchemaTitle("Ignore missing read permissions tables")
    @JsonSchemaDescription("Ignore tables with missing scan/read permissions")
    @JsonSchemaInject(json = """{"default":false}""")
    var ignoreMissingReadPermissionsTables: Boolean? = null
}

/**
 * The `credentials` oneOf. The `auth_type` discriminator is synthesized by Jackson;
 * [DynamoDbSpecificationExtender] renders it as `const` like the legacy spec does.
 */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = CredentialsSpecification.AUTH_TYPE)
@JsonSubTypes(
    JsonSubTypes.Type(value = UserCredentialsSpecification::class, name = "User"),
    JsonSubTypes.Type(value = RoleCredentialsSpecification::class, name = "Role"),
)
// No title/description here: the generator would copy them onto every variant, which the legacy
// spec does not have. They are set on the `credentials` property instead.
sealed interface CredentialsSpecification {
    companion object {
        const val AUTH_TYPE = "auth_type"
    }
}

/** Static access key authentication. */
@JsonSchemaTitle("Authenticate via Access Keys")
// The legacy spec declares this variant as `"type": ["null", "object"]`; kept for parity.
@JsonSchemaInject(json = """{"type":["null","object"]}""")
@JsonPropertyOrder(value = ["access_key_id", "secret_access_key"])
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class UserCredentialsSpecification : CredentialsSpecification {
    @JsonProperty("access_key_id")
    @JsonSchemaTitle("Dynamodb Key Id")
    @JsonSchemaDescription(
        "The access key id to access Dynamodb. Airbyte requires read permissions to the database",
    )
    @JsonSchemaInject(
        json = """{"order":1,"airbyte_secret":true,"examples":["A012345678910EXAMPLE"]}""",
    )
    lateinit var accessKeyId: String

    @JsonProperty("secret_access_key")
    @JsonSchemaTitle("Dynamodb Access Key")
    @JsonSchemaDescription("The corresponding secret to the access key id.")
    @JsonSchemaInject(
        json =
            """{"order":2,"airbyte_secret":true,"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"]}""",
    )
    lateinit var secretAccessKey: String
}

/**
 * Role-based authentication: credentials come from the AWS SDK default provider chain (environment
 * variables, web identity token / IRSA, ECS or EC2 instance profile, ...).
 */
@JsonSchemaTitle("Role Based Authentication")
class RoleCredentialsSpecification : CredentialsSpecification
