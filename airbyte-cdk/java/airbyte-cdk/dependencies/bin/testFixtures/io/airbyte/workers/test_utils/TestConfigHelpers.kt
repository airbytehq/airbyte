/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.test_utils

import io.airbyte.commons.json.Jsons
import io.airbyte.configoss.*
import io.airbyte.protocol.models.*
import java.util.*
import java.util.List
import java.util.Map
import org.apache.commons.lang3.tuple.ImmutablePair

object TestConfigHelpers {
    private const val CONNECTION_NAME = "favorite_color_pipe"
    private const val STREAM_NAME = "user_preferences"
    private const val FIELD_NAME = "favorite_color"
    private const val LAST_SYNC_TIME: Long = 1598565106

    @JvmOverloads
    fun createSyncConfig(
        multipleNamespaces: Boolean = false
    ): ImmutablePair<Void, StandardSyncInput> {
        val workspaceId = UUID.randomUUID()
        val sourceDefinitionId = UUID.randomUUID()
        val sourceId = UUID.randomUUID()
        val destinationDefinitionId = UUID.randomUUID()
        val destinationId = UUID.randomUUID()
        val normalizationOperationId = UUID.randomUUID()
        val dbtOperationId = UUID.randomUUID()

        val sourceConnection = Jsons.jsonNode(Map.of("apiKey", "123", "region", "us-east"))

        val destinationConnection =
            Jsons.jsonNode(Map.of("username", "airbyte", "token", "anau81b"))

        val sourceConnectionConfig =
            SourceConnection()
                .withConfiguration(sourceConnection)
                .withWorkspaceId(workspaceId)
                .withSourceDefinitionId(sourceDefinitionId)
                .withSourceId(sourceId)
                .withTombstone(false)

        val destinationConnectionConfig =
            DestinationConnection()
                .withConfiguration(destinationConnection)
                .withWorkspaceId(workspaceId)
                .withDestinationDefinitionId(destinationDefinitionId)
                .withDestinationId(destinationId)
                .withTombstone(false)

        val normalizationOperation =
            StandardSyncOperation()
                .withOperationId(normalizationOperationId)
                .withName("Normalization")
                .withOperatorType(StandardSyncOperation.OperatorType.NORMALIZATION)
                .withOperatorNormalization(
                    OperatorNormalization().withOption(OperatorNormalization.Option.BASIC)
                )
                .withTombstone(false)

        val customDbtOperation =
            StandardSyncOperation()
                .withOperationId(dbtOperationId)
                .withName("Custom Transformation")
                .withOperatorType(StandardSyncOperation.OperatorType.DBT)
                .withOperatorDbt(
                    OperatorDbt()
                        .withDockerImage("docker")
                        .withDbtArguments("--help")
                        .withGitRepoUrl("git url")
                        .withGitRepoBranch("git url")
                )
                .withTombstone(false)

        val catalog = ConfiguredAirbyteCatalog()
        if (multipleNamespaces) {
            val streamOne =
                ConfiguredAirbyteStream()
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME,
                            "namespace",
                            Field.of(FIELD_NAME, JsonSchemaType.STRING)
                        )
                    )
            val streamTwo =
                ConfiguredAirbyteStream()
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME,
                            "namespace2",
                            Field.of(FIELD_NAME, JsonSchemaType.STRING)
                        )
                    )

            val streams = List.of(streamOne, streamTwo)
            catalog.withStreams(streams)
        } else {
            val stream =
                ConfiguredAirbyteStream()
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME,
                            Field.of(FIELD_NAME, JsonSchemaType.STRING)
                        )
                    )
            catalog.withStreams(listOf(stream))
        }

        val stateValue = Jsons.serialize(Map.of("lastSync", LAST_SYNC_TIME.toString()))

        val state = State().withState(Jsons.jsonNode(stateValue))

        val syncInput =
            StandardSyncInput()
                .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.SOURCE)
                .withPrefix(CONNECTION_NAME)
                .withSourceId(sourceId)
                .withDestinationId(destinationId)
                .withDestinationConfiguration(destinationConnectionConfig.configuration)
                .withCatalog(catalog)
                .withSourceConfiguration(sourceConnectionConfig.configuration)
                .withState(state)
                .withOperationSequence(List.of(normalizationOperation, customDbtOperation))
                .withWorkspaceId(workspaceId)

        return ImmutablePair(null, syncInput)
    }
}
