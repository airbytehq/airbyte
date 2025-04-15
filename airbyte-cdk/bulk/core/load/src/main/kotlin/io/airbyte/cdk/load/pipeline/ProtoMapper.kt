/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.protocol.AirbyteRecord.AirbyteValue
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.security.MessageDigest

enum class ProtoDataType {
    STRING,
    BOOLEAN,
    INTEGER,
    NUMBER,
    BINARY,
}

abstract class ProtoMapper {
    internal val fakeSortedCatalog: List<Pair<String, ProtoDataType>> =
        listOf(
            Pair("occupation", ProtoDataType.STRING),
            Pair("gender", ProtoDataType.STRING),
            Pair("global_id", ProtoDataType.INTEGER),
            Pair("academic_degree", ProtoDataType.STRING),
            Pair("weight", ProtoDataType.NUMBER),
            Pair("created_at", ProtoDataType.STRING),
            Pair("language", ProtoDataType.STRING),
            Pair("telephone", ProtoDataType.STRING),
            Pair("title", ProtoDataType.STRING),
            Pair("updated_at", ProtoDataType.STRING),
            Pair("nationality", ProtoDataType.STRING),
            Pair("blood_type", ProtoDataType.STRING),
            Pair("name", ProtoDataType.STRING),
            Pair("id", ProtoDataType.INTEGER),
            Pair("age", ProtoDataType.INTEGER),
            Pair("email", ProtoDataType.STRING),
            Pair("height", ProtoDataType.NUMBER),
        )

    val finalSchema: List<Pair<String, ProtoDataType>> = mapSchema(fakeSortedCatalog)

    /** Called once to get the modified schema. */
    abstract fun mapSchema(
        schemaIn: List<Pair<String, ProtoDataType>>,
    ): List<Pair<String, ProtoDataType>>

    /**
     * Called per record to transform that data. Changes must match the schema changes or everything
     * will explode. You may safely mutate the list in place.
     */
    abstract fun mapData(dataIn: MutableList<AirbyteValue>): MutableList<AirbyteValue>
}

@Singleton
@Secondary
class IdentityProtoMapper : ProtoMapper() {
    override fun mapSchema(
        schemaIn: List<Pair<String, ProtoDataType>>,
    ): List<Pair<String, ProtoDataType>> = schemaIn

    override fun mapData(dataIn: MutableList<AirbyteValue>): MutableList<AirbyteValue> = dataIn
}

@Singleton
@Primary
class HashingProtoMapper : ProtoMapper() {
    override fun mapSchema(
        schemaIn: List<Pair<String, ProtoDataType>>,
    ): List<Pair<String, ProtoDataType>> = schemaIn

    override fun mapData(dataIn: MutableList<AirbyteValue>): MutableList<AirbyteValue> {
        val emailIndex = fakeSortedCatalog.indexOfFirst { it.first == "email" }
        val emailValue = dataIn.get(emailIndex)
        dataIn[emailIndex] =
            AirbyteValue.newBuilder(emailValue)
                .setString(
                    String(MessageDigest.getInstance("SHA-256").digest(emailValue.toByteArray())),
                )
                .build()
        return dataIn
    }
}
