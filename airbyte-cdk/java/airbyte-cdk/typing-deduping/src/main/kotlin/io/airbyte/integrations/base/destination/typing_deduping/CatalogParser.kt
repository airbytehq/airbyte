/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler.Companion.addStringForDeinterpolation
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.Optional
import java.util.function.Consumer
import org.apache.commons.codec.digest.DigestUtils

private val LOGGER = KotlinLogging.logger {}

class CatalogParser
@JvmOverloads
constructor(
    private val sqlGenerator: SqlGenerator,
    private val defaultNamespace: String,
    private val rawNamespace: String = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE,
) {
    fun parseCatalog(orginalCatalog: ConfiguredAirbyteCatalog): ParsedCatalog {
        // Don't mutate the original catalog, just operate on a copy of it
        // This is... probably the easiest way we have to deep clone a protocol model object?
        val catalog = Jsons.clone(orginalCatalog)
        catalog.streams.onEach {
            // Overwrite null namespaces
            if (it.stream.namespace.isNullOrEmpty()) {
                it.stream.namespace = defaultNamespace
            }
            // The refreshes project is the beginning of the end for OVERWRITE syncs.
            // The sync mode still exists, but we are fully dependent on min_generation to trigger
            // overwrite logic.
            if (it.destinationSyncMode == DestinationSyncMode.OVERWRITE) {
                it.destinationSyncMode = DestinationSyncMode.APPEND
            }
        }

        // this code is bad and I feel bad
        // it's mostly a port of the old normalization logic to prevent tablename collisions.
        // tbh I have no idea if it works correctly.
        val streamConfigs: MutableList<StreamConfig> = ArrayList()
        for (stream in catalog.streams) {
            val originalStreamConfig = toStreamConfig(stream)
            val actualStreamConfig: StreamConfig
            // Use empty string quote because we don't really care
            if (
                streamConfigs.any { s: StreamConfig ->
                    s.id.finalTableId("") == originalStreamConfig.id.finalTableId("")
                } ||
                    streamConfigs.any { s: StreamConfig ->
                        s.id.rawTableId("") == originalStreamConfig.id.rawTableId("")
                    }
            ) {
                val originalNamespace = stream.stream.namespace
                val originalName = stream.stream.name

                LOGGER.info { "Detected table name collision for $originalNamespace.$originalName" }

                // ... this logic is ported from legacy normalization, and maybe should change?
                // We're taking a hash of the quoted namespace and the unquoted stream name
                val hash =
                    DigestUtils.sha1Hex(
                            "${originalStreamConfig.id.finalNamespace}&airbyte&$originalName"
                        )
                        .substring(0, 3)
                val newName = "${originalName}_$hash"
                actualStreamConfig =
                    originalStreamConfig.copy(
                        id =
                            sqlGenerator.buildStreamId(
                                originalNamespace,
                                newName,
                                rawNamespace,
                            ),
                    )
            } else {
                actualStreamConfig = originalStreamConfig
            }
            streamConfigs.add(
                actualStreamConfig.copy(
                    // If we had collisions, we modified the stream name.
                    // Revert those changes.
                    id =
                        actualStreamConfig.id.copy(
                            originalName = stream.stream.name,
                            originalNamespace = stream.stream.namespace,
                        ),
                ),
            )

            // Populate some interesting strings into the exception handler string deinterpolator
            addStringForDeinterpolation(actualStreamConfig.id.rawNamespace)
            addStringForDeinterpolation(actualStreamConfig.id.rawName)
            addStringForDeinterpolation(actualStreamConfig.id.finalNamespace)
            addStringForDeinterpolation(actualStreamConfig.id.finalName)
            addStringForDeinterpolation(actualStreamConfig.id.originalNamespace)
            addStringForDeinterpolation(actualStreamConfig.id.originalName)
            actualStreamConfig.columns.keys.forEach(
                Consumer { columnId: ColumnId ->
                    addStringForDeinterpolation(columnId.name)
                    addStringForDeinterpolation(columnId.originalName)
                }
            )
            // It's (unfortunately) possible for a cursor/PK to be declared that don't actually
            // exist in the
            // schema.
            // Add their strings explicitly.
            actualStreamConfig.cursor.ifPresent { cursor: ColumnId ->
                addStringForDeinterpolation(cursor.name)
                addStringForDeinterpolation(cursor.originalName)
            }
            actualStreamConfig.primaryKey.forEach(
                Consumer { pk: ColumnId ->
                    addStringForDeinterpolation(pk.name)
                    addStringForDeinterpolation(pk.originalName)
                }
            )
        }
        LOGGER.info { "Running sync with stream configs: $streamConfigs" }
        return ParsedCatalog(streamConfigs)
    }

    @VisibleForTesting
    fun toStreamConfig(stream: ConfiguredAirbyteStream): StreamConfig {
        if (stream.generationId == null) {
            throw ConfigErrorException(
                "You must upgrade your platform version to use this connector version. Either downgrade your connector or upgrade platform to 0.63.0"
            )
        }
        if (
            stream.minimumGenerationId != 0.toLong() &&
                stream.minimumGenerationId != stream.generationId
        ) {
            throw UnsupportedOperationException("Hybrid refreshes are not yet supported.")
        }

        val airbyteColumns =
            when (
                val schema: AirbyteType =
                    AirbyteType.Companion.fromJsonSchema(stream.stream.jsonSchema)
            ) {
                is Struct -> schema.properties
                is Union -> schema.asColumns()
                else -> throw IllegalArgumentException("Top-level schema must be an object")
            }

        require(!stream.primaryKey.any { key: List<String> -> key.size > 1 }) {
            "Only top-level primary keys are supported"
        }
        val primaryKey =
            stream.primaryKey.map { key: List<String> -> sqlGenerator.buildColumnId(key[0]) }

        require(stream.cursorField.size <= 1) { "Only top-level cursors are supported" }
        val cursor: Optional<ColumnId> =
            if (stream.cursorField.isNotEmpty()) {
                Optional.of(sqlGenerator.buildColumnId(stream.cursorField[0]))
            } else {
                Optional.empty()
            }

        val columns = resolveColumnCollisions(airbyteColumns, stream)

        return StreamConfig(
            sqlGenerator.buildStreamId(stream.stream.namespace, stream.stream.name, rawNamespace),
            stream.destinationSyncMode,
            primaryKey,
            cursor,
            columns,
            stream.generationId,
            stream.minimumGenerationId,
            stream.syncId,
        )
    }

    /**
     * This code is really bad and I'm not convinced we need to preserve this behavior. As with the
     * tablename collisions thing above - we're trying to preserve legacy normalization's naming
     * conventions here.
     */
    private fun resolveColumnCollisions(
        airbyteColumns: LinkedHashMap<String, AirbyteType>,
        stream: ConfiguredAirbyteStream
    ): LinkedHashMap<ColumnId, AirbyteType> {
        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        for ((key, value) in airbyteColumns) {
            val originalColumnId = sqlGenerator.buildColumnId(key)
            var columnId: ColumnId
            if (
                columns.keys.none { c: ColumnId ->
                    c.canonicalName == originalColumnId.canonicalName
                }
            ) {
                // None of the existing columns have the same name. We can add this new column
                // as-is.
                columnId = originalColumnId
            } else {
                LOGGER.info {
                    "Detected column name collision for ${stream.stream.namespace}.${stream.stream.name}.$key"
                }
                // One of the existing columns has the same name. We need to handle this collision.
                // Append _1, _2, _3, ... to the column name until we find one that doesn't collide.
                var i = 1
                while (true) {
                    columnId = sqlGenerator.buildColumnId(key, "_$i")

                    // Verify that we're making progress, e.g. we haven't immediately truncated away
                    // the suffix.
                    if (columnId.canonicalName == originalColumnId.canonicalName) {
                        // If we're not making progress, do a more powerful mutation instead of
                        // appending numbers.
                        // Assume that we're being truncated, and that the column ID's name is the
                        // maximum length.
                        columnId =
                            superResolveColumnCollisions(
                                originalColumnId,
                                columns,
                                originalColumnId.name.length
                            )
                        break
                    }

                    val canonicalName = columnId.canonicalName
                    if (columns.keys.none { c: ColumnId -> c.canonicalName == canonicalName }) {
                        break
                    } else {
                        i++
                    }
                }
                // But we need to keep the original name so that we can still fetch it out of the
                // JSON records.
                columnId =
                    ColumnId(
                        columnId.name,
                        originalColumnId.originalName,
                        columnId.canonicalName,
                    )
            }

            columns[columnId] = value
        }
        return columns
    }

    /**
     * Generate a name of the format `<prefix><length><suffix>`. E.g. for affixLength=3:
     * "veryLongName" -> "ver6ame" This is based on the "i18n"-ish naming convention.
     *
     * @param columnId The column that we're trying to add
     * @param columns The columns that we've already added
     */
    private fun superResolveColumnCollisions(
        columnId: ColumnId,
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        maximumColumnNameLength: Int
    ): ColumnId {
        val originalColumnName = columnId.originalName

        var newColumnId = columnId
        // Assume that the <length> portion can be expressed in at most 5 characters.
        // If someone is giving us a column name that's longer than 99999 characters,
        // that's just being silly.
        val affixLength = (maximumColumnNameLength - 5) / 2
        // If, after reserving 5 characters for the length, we can't fit the affixes,
        // just give up. That means the destination is trying to restrict us to a
        // 6-character column name, which is just silly.
        if (affixLength <= 0) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: ${newColumnId.originalName}. We recommend removing this column to continue syncing."
            )
        }
        val prefix = originalColumnName.substring(0, affixLength)
        val suffix =
            originalColumnName.substring(
                originalColumnName.length - affixLength,
                originalColumnName.length
            )
        val length = originalColumnName.length - 2 * affixLength
        newColumnId = sqlGenerator.buildColumnId("$prefix$length$suffix")
        // if there's _still_ a collision after this, just give up.
        // we could try to be more clever, but this is already a pretty rare case.
        if (columns.keys.any { c: ColumnId -> c.canonicalName == newColumnId.canonicalName }) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: ${newColumnId.originalName}. We recommend removing this column to continue syncing."
            )
        }
        return newColumnId
    }

    companion object {}
}
