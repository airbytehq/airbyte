/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss

import io.airbyte.commons.json.JsonSchemas.prepareSchemas
import java.io.File
import java.nio.file.Path
import java.util.function.Function

enum class ConfigSchema : AirbyteConfig {
    // workspace
    WORKSPACE_WEBHOOK_OPERATION_CONFIGS(
        "WebhookOperationConfigs.yaml",
        WebhookOperationConfigs::class.java
    ),

    // source
    STANDARD_SOURCE_DEFINITION(
        "StandardSourceDefinition.yaml",
        StandardSourceDefinition::class.java,
        Function<StandardSourceDefinition, String> {
            standardSourceDefinition: StandardSourceDefinition ->
            standardSourceDefinition.sourceDefinitionId.toString()
        },
        "sourceDefinitionId"
    ),
    SOURCE_CONNECTION(
        "SourceConnection.yaml",
        SourceConnection::class.java,
        Function<SourceConnection, String> { sourceConnection: SourceConnection ->
            sourceConnection.sourceId.toString()
        },
        "sourceId"
    ),

    // destination
    STANDARD_DESTINATION_DEFINITION(
        "StandardDestinationDefinition.yaml",
        StandardDestinationDefinition::class.java,
        Function<StandardDestinationDefinition, String> {
            standardDestinationDefinition: StandardDestinationDefinition ->
            standardDestinationDefinition.destinationDefinitionId.toString()
        },
        "destinationDefinitionId"
    ),
    DESTINATION_CONNECTION(
        "DestinationConnection.yaml",
        DestinationConnection::class.java,
        Function<DestinationConnection, String> { destinationConnection: DestinationConnection ->
            destinationConnection.destinationId.toString()
        },
        "destinationId"
    ),
    STANDARD_SYNC_OPERATION(
        "StandardSyncOperation.yaml",
        StandardSyncOperation::class.java,
        Function<StandardSyncOperation, String> { standardSyncOperation: StandardSyncOperation ->
            standardSyncOperation.operationId.toString()
        },
        "operationId"
    ),
    SOURCE_OAUTH_PARAM(
        "SourceOAuthParameter.yaml",
        SourceOAuthParameter::class.java,
        Function<SourceOAuthParameter, String> { sourceOAuthParameter: SourceOAuthParameter ->
            sourceOAuthParameter.oauthParameterId.toString()
        },
        "oauthParameterId"
    ),
    DESTINATION_OAUTH_PARAM(
        "DestinationOAuthParameter.yaml",
        DestinationOAuthParameter::class.java,
        Function<DestinationOAuthParameter, String> {
            destinationOAuthParameter: DestinationOAuthParameter ->
            destinationOAuthParameter.oauthParameterId.toString()
        },
        "oauthParameterId"
    ),

    // worker
    STANDARD_SYNC_INPUT("StandardSyncInput.yaml", StandardSyncInput::class.java),
    STATE("State.yaml", State::class.java);

    private val schemaFilename: String
    private val className: Class<*>
    private val extractId: Function<*, String>
    override val idFieldName: String?

    constructor(
        schemaFilename: String,
        className: Class<*>,
        extractId: Function<*, String>,
        idFieldName: String
    ) {
        this.schemaFilename = schemaFilename
        this.className = className
        this.extractId = extractId
        this.idFieldName = idFieldName
    }

    constructor(schemaFilename: String, className: Class<*>) {
        this.schemaFilename = schemaFilename
        this.className = className
        extractId = Function { _: Any ->
            throw RuntimeException(className.getSimpleName() + " doesn't have an id")
        }
        idFieldName = null
    }

    override val configSchemaFile: File
        get() = KNOWN_SCHEMAS_ROOT.resolve(schemaFilename).toFile()

    override fun <T> getClassName(): Class<T> {
        @Suppress("unchecked_cast") return className as Class<T>
    }

    override fun <T> getId(config: T): String {
        if (getClassName<Any>().isInstance(config)) {
            @Suppress("unchecked_cast") return (extractId as Function<T, String>).apply(config)
        }
        throw RuntimeException(
            "Object: " + config + " is not instance of class " + getClassName<Any>().name
        )
    }

    override fun getName(): String {
        return name
    }

    companion object {
        val KNOWN_SCHEMAS_ROOT: Path = prepareSchemas("types", ConfigSchema::class.java)
    }
}
