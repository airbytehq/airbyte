/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler.Companion.addStringForDeinterpolation
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.*
import java.util.function.Consumer
import org.apache.commons.codec.digest.DigestUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class CatalogParser
@JvmOverloads
constructor(
    private val sqlGenerator: SqlGenerator,
    private val rawNamespace: String = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
) {
    fun parseCatalog(catalog: ConfiguredAirbyteCatalog): ParsedCatalog {
        // this code is bad and I feel bad
        // it's mostly a port of the old normalization logic to prevent tablename collisions.
        // tbh I have no idea if it works correctly.
        val streamConfigs: MutableList<StreamConfig> = ArrayList()
        for (stream in catalog.streams) {
            val originalStreamConfig = toStreamConfig(stream)
            val actualStreamConfig: StreamConfig
            // Use empty string quote because we don't really care
            if (
                streamConfigs.stream().anyMatch { s: StreamConfig ->
                    s.id.finalTableId("") == originalStreamConfig.id.finalTableId("")
                } ||
                    streamConfigs.stream().anyMatch { s: StreamConfig ->
                        s.id.rawTableId("") == originalStreamConfig.id.rawTableId("")
                    }
            ) {
                val originalNamespace = stream.stream.namespace
                val originalName = stream.stream.name

                LOGGER.info(
                    "Detected table name collision for {}.{}",
                    originalNamespace,
                    originalName
                )

                // ... this logic is ported from legacy normalization, and maybe should change?
                // We're taking a hash of the quoted namespace and the unquoted stream name
                val hash =
                    DigestUtils.sha1Hex(
                            originalStreamConfig.id!!.finalNamespace + "&airbyte&" + originalName
                        )
                        .substring(0, 3)
                val newName = originalName + "_" + hash
                actualStreamConfig =
                    StreamConfig(
                        sqlGenerator.buildStreamId(originalNamespace, newName, rawNamespace),
                        originalStreamConfig.syncMode,
                        originalStreamConfig.destinationSyncMode,
                        originalStreamConfig.primaryKey,
                        originalStreamConfig.cursor,
                        originalStreamConfig.columns
                    )
            } else {
                actualStreamConfig = originalStreamConfig
            }
            streamConfigs.add(actualStreamConfig)

            // Populate some interesting strings into the exception handler string deinterpolator
            addStringForDeinterpolation(actualStreamConfig.id!!.rawNamespace)
            addStringForDeinterpolation(actualStreamConfig.id!!.rawName)
            addStringForDeinterpolation(actualStreamConfig.id!!.finalNamespace)
            addStringForDeinterpolation(actualStreamConfig.id!!.finalName)
            addStringForDeinterpolation(actualStreamConfig.id!!.originalNamespace)
            addStringForDeinterpolation(actualStreamConfig.id!!.originalName)
            actualStreamConfig.columns!!
                .keys
                .forEach(
                    Consumer { columnId: ColumnId? ->
                        addStringForDeinterpolation(columnId!!.name)
                        addStringForDeinterpolation(columnId.originalName)
                    }
                )
            // It's (unfortunately) possible for a cursor/PK to be declared that don't actually
            // exist in the
            // schema.
            // Add their strings explicitly.
            actualStreamConfig.cursor!!.ifPresent { cursor: ColumnId ->
                addStringForDeinterpolation(cursor.name)
                addStringForDeinterpolation(cursor.originalName)
            }
            actualStreamConfig.primaryKey!!.forEach(
                Consumer { pk: ColumnId ->
                    addStringForDeinterpolation(pk.name)
                    addStringForDeinterpolation(pk.originalName)
                }
            )
        }
        return ParsedCatalog(streamConfigs)
    }

    // TODO maybe we should extract the column collision stuff to a separate method, since that's
    // the
    // interesting bit
    @VisibleForTesting
    fun toStreamConfig(stream: ConfiguredAirbyteStream): StreamConfig {
        val schema: AirbyteType = AirbyteType.Companion.fromJsonSchema(stream.stream.jsonSchema)
        val airbyteColumns =
            if (schema is Struct) {
                schema.properties
            } else if (schema is Union) {
                schema.asColumns()
            } else {
                throw IllegalArgumentException("Top-level schema must be an object")
            }

        require(!stream.primaryKey.stream().anyMatch { key: List<String?> -> key.size > 1 }) {
            "Only top-level primary keys are supported"
        }
        val primaryKey =
            stream.primaryKey
                .stream()
                .map { key: List<String> -> sqlGenerator.buildColumnId(key[0]) }
                .toList()

        require(stream.cursorField.size <= 1) { "Only top-level cursors are supported" }
        val cursor: Optional<ColumnId>
        if (stream.cursorField.size > 0) {
            cursor = Optional.of(sqlGenerator.buildColumnId(stream.cursorField[0])!!)
        } else {
            cursor = Optional.empty()
        }

        // this code is really bad and I'm not convinced we need to preserve this behavior.
        // as with the tablename collisions thing above - we're trying to preserve legacy
        // normalization's
        // naming conventions here.
        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        for ((key, value) in airbyteColumns) {
            val originalColumnId = sqlGenerator.buildColumnId(key)
            var columnId: ColumnId?
            if (
                columns.keys.stream().noneMatch { c: ColumnId ->
                    c.canonicalName == originalColumnId.canonicalName
                }
            ) {
                // None of the existing columns have the same name. We can add this new column
                // as-is.
                columnId = originalColumnId
            } else {
                LOGGER.info(
                    "Detected column name collision for {}.{}.{}",
                    stream.stream.namespace,
                    stream.stream.name,
                    key
                )
                // One of the existing columns has the same name. We need to handle this collision.
                // Append _1, _2, _3, ... to the column name until we find one that doesn't collide.
                var i = 1
                while (true) {
                    columnId = sqlGenerator.buildColumnId(key, "_$i")
                    val canonicalName = columnId!!.canonicalName
                    if (
                        columns.keys.stream().noneMatch { c: ColumnId ->
                            c.canonicalName == canonicalName
                        }
                    ) {
                        break
                    } else {
                        i++
                    }
                }
                // But we need to keep the original name so that we can still fetch it out of the
                // JSON records.
                columnId =
                    ColumnId(
                        columnId!!.name,
                        originalColumnId!!.originalName,
                        columnId.canonicalName
                    )
            }

            columns[columnId] = value
        }

        return StreamConfig(
            sqlGenerator.buildStreamId(stream.stream.namespace, stream.stream.name, rawNamespace),
            stream.syncMode,
            stream.destinationSyncMode,
            primaryKey,
            cursor,
            columns
        )
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(CatalogParser::class.java)
    }
}
