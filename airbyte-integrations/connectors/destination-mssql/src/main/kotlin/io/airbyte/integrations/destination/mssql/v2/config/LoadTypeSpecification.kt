/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageSpecification

/**
 * Describes a specification for configuring how data should be loaded into MSSQL (e.g., via INSERT
 * or BULK). Classes implementing this interface must define a [loadType] and be able to produce an
 * [MSSQLLoadTypeConfiguration].
 */
interface LoadTypeSpecification {

    @get:JsonSchemaTitle("Load Type")
    @get:JsonPropertyDescription(
        "Specifies the type of load mechanism (e.g., BULK, INSERT) and its associated configuration."
    )
    @get:JsonProperty("load_type")
    val loadType: LoadType

    /**
     * Produces a [MSSQLLoadTypeConfiguration] object describing how the MSSQL load should be
     * performed, based on whether the load is BULK or INSERT.
     */
    fun toLoadConfiguration(): MSSQLLoadTypeConfiguration {
        val loadTypeConfig: LoadTypeConfiguration =
            when (val lt = loadType) {
                is BulkLoadSpecification -> {
                    BulkLoadConfiguration(
                        accountName = lt.azureBlobStorageAccountName,
                        containerName = lt.azureBlobStorageContainerName,
                        sharedAccessSignature = lt.azureBlobStorageSharedAccessSignature,
                        bulkLoadDataSource = lt.bulkLoadDataSource,
                        validateValuesPreLoad = lt.validateValuesPreLoad
                    )
                }
                is InsertLoadSpecification -> InsertLoadTypeConfiguration()
            }
        return MSSQLLoadTypeConfiguration(loadTypeConfig)
    }
}

/**
 * Represents the method by which MSSQL will load data. Currently, supports:
 * - [InsertLoadSpecification]: row-by-row inserts
 * - [BulkLoadSpecification]: bulk loading using Azure Blob Storage
 */
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "load_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = InsertLoadSpecification::class, name = "INSERT"),
    JsonSubTypes.Type(value = BulkLoadSpecification::class, name = "BULK"),
)
@JsonSchemaTitle("MSSQL Load Type")
@JsonSchemaDescription(
    "Determines the specific implementation used by the MSSQL destination to load data."
)
sealed class LoadType(@JsonSchemaTitle("Load Type") open val loadType: Type) {

    /** Enum of possible load operations in MSSQL: INSERT or BULK. */
    enum class Type(@get:JsonValue val loadTypeName: String) {
        INSERT("INSERT"),
        BULK("BULK")
    }
}

/** Basic configuration for the INSERT load mechanism in MSSQL. */
@JsonSchemaTitle("Insert Load")
@JsonSchemaDescription("Configuration details for using the INSERT loading mechanism.")
class InsertLoadSpecification(
    @JsonSchemaTitle("Load Type")
    @JsonProperty("load_type")
    @JsonSchemaInject(json = """{"order": 0}""")
    override val loadType: Type = Type.INSERT,
) : LoadType(loadType)

/** Configuration for the BULK load mechanism, leveraging Azure Blob Storage. */
@JsonSchemaTitle("Bulk Load")
@JsonSchemaDescription("Configuration details for using the BULK loading mechanism.")
class BulkLoadSpecification(
    @JsonSchemaTitle("Load Type")
    @JsonProperty("load_type")
    @JsonSchemaInject(json = """{"order": 0}""")
    override val loadType: Type = Type.BULK,
    @get:JsonSchemaTitle("Azure Blob Storage Account Name")
    @get:JsonPropertyDescription(
        "The name of the Azure Blob Storage account. " +
            "See: https://learn.microsoft.com/azure/storage/blobs/storage-blobs-introduction#storage-accounts"
    )
    @get:JsonProperty("azure_blob_storage_account_name")
    @JsonSchemaInject(
        json =
            """{
            "examples": ["mystorageaccount"],
            "order": 1,
            "always_show": true
        }"""
    )
    override val azureBlobStorageAccountName: String,
    @get:JsonSchemaTitle("Azure Blob Storage Container Name")
    @get:JsonPropertyDescription(
        "The name of the Azure Blob Storage container. " +
            "See: https://learn.microsoft.com/azure/storage/blobs/storage-blobs-introduction#containers"
    )
    @get:JsonProperty("azure_blob_storage_container_name")
    @JsonSchemaInject(
        json = """{
            "order": 2,
            "always_show": true
        }"""
    )
    override val azureBlobStorageContainerName: String,
    @get:JsonSchemaTitle("Shared Access Signature")
    @get:JsonPropertyDescription(
        "A shared access signature (SAS) provides secure delegated access to resources " +
            "in your storage account. See: https://learn.microsoft.com/azure/storage/common/storage-sas-overview"
    )
    @get:JsonProperty("shared_access_signature")
    @JsonSchemaInject(
        json =
            """{
            "examples": ["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],
            "order": 3,
            "airbyte_secret": true,
            "always_show": true
        }"""
    )
    override val azureBlobStorageSharedAccessSignature: String,
    @get:JsonSchemaTitle("BULK Load Data Source")
    @get:JsonPropertyDescription(
        "Specifies the external data source name configured in MSSQL, which references " +
            "the Azure Blob container. See: https://learn.microsoft.com/sql/t-sql/statements/bulk-insert-transact-sql"
    )
    @get:JsonProperty("bulk_load_data_source")
    @JsonSchemaInject(
        json =
            """{
            "examples": ["MyAzureBlobStorage"],
            "order": 4,
            "always_show": true
        }"""
    )
    val bulkLoadDataSource: String,
    @get:JsonSchemaTitle("Pre-Load Value Validation")
    @get:JsonPropertyDescription(
        "When enabled, Airbyte will validate all values before loading them into the destination table. " +
            "This provides stronger data integrity guarantees but may significantly impact performance."
    )
    @get:JsonProperty("bulk_load_validate_values_pre_load")
    @JsonSchemaInject(
        json =
            """{
        "examples": ["false"],
        "default": false,
        "type": "boolean",
        "order": 5,
        "always_show": false
    }"""
    )
    val validateValuesPreLoad: Boolean?
) : LoadType(loadType), AzureBlobStorageSpecification

/**
 * A marker interface for classes that hold the load configuration details. This helps unify both
 * `InsertLoadTypeConfiguration` and `BulkLoadConfiguration`.
 */
sealed interface LoadTypeConfiguration

/** A unified configuration object for MSSQL load settings. */
@JsonSchemaTitle("MSSQL Load Configuration")
@JsonSchemaDescription("Encapsulates the selected MSSQL load mechanism and its settings.")
data class MSSQLLoadTypeConfiguration(
    @JsonSchemaTitle("MSSQL Load Type Configuration")
    @JsonPropertyDescription("Specific configuration details of the chosen MSSQL load mechanism.")
    val loadTypeConfiguration: LoadTypeConfiguration
)

/**
 * Configuration for the INSERT load approach. Typically minimal or empty, but can be expanded if
 * needed in the future.
 */
@JsonSchemaTitle("INSERT Load Configuration")
@JsonSchemaDescription("INSERT-specific configuration details for MSSQL.")
data class InsertLoadTypeConfiguration(val ignored: String = "") : LoadTypeConfiguration

/** Configuration for the BULK load approach, matching fields from [BulkLoadSpecification]. */
@JsonSchemaTitle("BULK Load Configuration")
@JsonSchemaDescription("BULK-specific configuration details for MSSQL.")
data class BulkLoadConfiguration(
    val accountName: String,
    val containerName: String,
    val sharedAccessSignature: String,
    val bulkLoadDataSource: String,
    val validateValuesPreLoad: Boolean?
) : LoadTypeConfiguration

/**
 * Provides an MSSQLLoadTypeConfiguration, typically used by higher-level components that need to
 * process MSSQL load logic at runtime.
 */
interface MSSQLLoadTypeConfigurationProvider {
    val mssqlLoadTypeConfiguration: MSSQLLoadTypeConfiguration
}
