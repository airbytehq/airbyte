/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
class RedshiftV2Specification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonPropertyDescription(
        "Host Endpoint of the Redshift Cluster (must include the cluster-id, region and end with .redshift.amazonaws.com)"
    )
    @JsonSchemaInject(json = """{"group": "connection", "order": 0}""")
    var host: String = ""

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonPropertyDescription("Port of the database.")
    @JsonSchemaInject(
        json =
            """{"group": "connection", "order": 1, "minimum": 0, "maximum": 65536, "default": 5439, "examples": ["5439"]}"""
    )
    var port: Int = 5439

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("Username to use to access the database.")
    @JsonSchemaInject(json = """{"group": "connection", "order": 2}""")
    var username: String = ""

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("Password associated with the username.")
    @JsonSchemaInject(json = """{"group": "connection", "order": 3, "airbyte_secret": true}""")
    var password: String = ""

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("Name of the database.")
    @JsonSchemaInject(json = """{"group": "connection", "order": 4}""")
    var database: String = ""

    @JsonProperty("schema")
    @JsonSchemaTitle("Default Schema")
    @JsonPropertyDescription(
        "The default schema tables are written to if the source does not specify a namespace. Unless specifically configured, the usual value for this field is \"public\"."
    )
    @JsonSchemaInject(
        json =
            """{"group": "connection", "order": 5, "examples": ["public"], "default": "public"}"""
    )
    var schema: String = "public"

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Params")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3)."
    )
    @JsonSchemaInject(json = """{"group": "connection", "order": 6}""")
    var jdbcUrlParams: String? = null

    @JsonProperty("uploading_method")
    @JsonSchemaTitle("Uploading Method")
    @JsonSchemaDescription("The way data will be uploaded to Redshift.")
    @JsonSchemaInject(json = """{"group": "connection", "order": 7, "display_type": "radio"}""")
    var uploadingMethod: UploadingMethodSpecification? = null

    @JsonProperty("drop_cascade")
    @JsonSchemaTitle("Drop tables with CASCADE. (WARNING! Risk of unrecoverable data loss)")
    @JsonPropertyDescription(
        "Drop tables with CASCADE. WARNING! This will delete all data in all dependent objects (views, etc.). Use with caution. This option is intended for usecases which can easily rebuild the dependent objects."
    )
    @JsonSchemaInject(json = """{"group": "tables", "order": 2, "default": false}""")
    var dropCascade: Boolean? = false

    @JsonProperty("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonSchemaDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, and if so, which kind of authentication to use."
    )
    @JsonSchemaInject(json = """{"group": "connection", "order": 8}""")
    var tunnelMethod: SshTunnelMethodConfiguration? = null
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "method",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = StandardSpecification::class, name = "Standard"),
    JsonSubTypes.Type(value = S3StagingSpecification::class, name = "S3 Staging"),
)
sealed class UploadingMethodSpecification(
    @Suppress("PropertyName") @param:JsonProperty("method") val method: UploadMethod
) {
    enum class UploadMethod(@get:JsonValue val methodName: String) {
        STANDARD("Standard"),
        S3_STAGING("S3 Staging"),
    }
}

@JsonSchemaTitle("Standard Inserts")
@JsonSchemaDescription(
    "Direct database inserts. This method is slower but requires no additional cloud resources."
)
class StandardSpecification : UploadingMethodSpecification(UploadMethod.STANDARD)

@JsonSchemaTitle("AWS S3 Staging")
@JsonSchemaDescription(
    "(recommended) Uploads data to S3 and then uses a COPY to insert the data into Redshift. COPY is recommended for production workloads for better speed and scalability."
)
class S3StagingSpecification(
    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription("The name of the staging S3 bucket.")
    @get:JsonProperty("s3_bucket_name")
    @get:JsonSchemaInject(json = """{"order": 0, "examples": ["airbyte.staging"]}""")
    val s3BucketName: String = "",
    @get:JsonSchemaTitle("S3 Bucket Path")
    @get:JsonPropertyDescription(
        "The directory under the S3 bucket where data will be written. If not provided, then defaults to the root directory."
    )
    @get:JsonProperty("s3_bucket_path")
    @get:JsonSchemaInject(json = """{"order": 1, "examples": ["data_sync/test"]}""")
    val s3BucketPath: String? = null,
    @get:JsonSchemaTitle("S3 Bucket Region")
    @get:JsonPropertyDescription("The region of the S3 staging bucket.")
    @get:JsonProperty("s3_bucket_region")
    @get:JsonSchemaInject(
        json =
            """{"order": 2, "default": "", "enum": ["", "af-south-1", "ap-east-1", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3", "ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4", "ca-central-1", "ca-west-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2", "eu-west-1", "eu-west-2", "eu-west-3", "il-central-1", "me-central-1", "me-south-1", "sa-east-1", "us-east-1", "us-east-2", "us-gov-east-1", "us-gov-west-1", "us-west-1", "us-west-2"]}"""
    )
    val s3BucketRegion: String = "",
    @get:JsonSchemaTitle("S3 Access Key Id")
    @get:JsonPropertyDescription(
        "This ID grants access to the above S3 staging bucket. Airbyte requires Read and Write permissions to the given bucket."
    )
    @get:JsonProperty("access_key_id")
    @get:JsonSchemaInject(json = """{"order": 3, "airbyte_secret": true}""")
    val accessKeyId: String = "",
    @get:JsonSchemaTitle("S3 Secret Access Key")
    @get:JsonPropertyDescription("The corresponding secret to the above access key id.")
    @get:JsonProperty("secret_access_key")
    @get:JsonSchemaInject(json = """{"order": 4, "airbyte_secret": true}""")
    val secretAccessKey: String = "",
    @get:JsonSchemaTitle("S3 Filename pattern")
    @get:JsonPropertyDescription(
        "The pattern allows you to set the file-name format for the S3 staging file(s)"
    )
    @get:JsonProperty("file_name_pattern")
    @get:JsonSchemaInject(
        json =
            """{"order": 5, "examples": ["{date}", "{date:yyyy_MM}", "{timestamp}", "{part_number}", "{sync_id}"]}"""
    )
    val fileNamePattern: String? = null,
    @get:JsonSchemaTitle("Purge Staging Files and Tables")
    @get:JsonPropertyDescription(
        "Whether to delete the staging files from S3 after completing the sync."
    )
    @get:JsonProperty("purge_staging_data")
    @get:JsonSchemaInject(json = """{"order": 6, "default": true}""")
    val purgeStagingData: Boolean? = true,
) : UploadingMethodSpecification(UploadMethod.S3_STAGING)

@Singleton
class RedshiftV2SpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
    override val groups =
        listOf(
            DestinationSpecificationExtension.Group("connection", "Connection"),
            DestinationSpecificationExtension.Group("tables", "Tables"),
        )
}
