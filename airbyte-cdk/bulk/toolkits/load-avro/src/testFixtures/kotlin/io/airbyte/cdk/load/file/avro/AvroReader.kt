/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.avro

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.UnionType
import java.io.Closeable
import java.io.InputStream
import kotlin.io.path.outputStream
import org.apache.avro.Schema
import org.apache.avro.file.DataFileReader
import org.apache.avro.generic.GenericDatumReader
import org.apache.avro.generic.GenericRecord

class AvroReader(
    private val dataFileReader: DataFileReader<GenericRecord>,
    private val tmpFile: java.io.File
) : Closeable {
    private fun read(): GenericRecord? {
        return if (dataFileReader.hasNext()) {
            dataFileReader.next()
        } else {
            null
        }
    }

    fun recordSequence(): Sequence<GenericRecord> {
        return generateSequence { read() }
    }

    override fun close() {
        dataFileReader.close()
        tmpFile.delete()
    }
}

fun InputStream.toAvroReader(descriptor: DestinationStream.Descriptor): AvroReader {
    val reader = GenericDatumReader<GenericRecord>()
    val tmpFile =
        kotlin.io.path.createTempFile(
            prefix = "${descriptor.namespace}.${descriptor.name}",
            suffix = ".avro"
        )
    tmpFile.outputStream().use { outputStream -> this.copyTo(outputStream) }
    val file = tmpFile.toFile()
    val dataFileReader = DataFileReader(file, reader)
    return AvroReader(dataFileReader, file)
}

fun toAirbyteType(schema: Schema): AirbyteType {
    return when (schema.type) {
        Schema.Type.STRING -> StringType
        Schema.Type.INT,
        Schema.Type.LONG -> IntegerType
        Schema.Type.FLOAT,
        Schema.Type.DOUBLE -> NumberType
        Schema.Type.BOOLEAN -> BooleanType
        Schema.Type.RECORD ->
            ObjectType(
                schema.fields.associateTo(linkedMapOf()) {
                    it.name() to FieldType(toAirbyteType(it.schema()), nullable = true)
                }
            )
        Schema.Type.ARRAY ->
            ArrayType(FieldType(toAirbyteType(schema.elementType), nullable = true))
        Schema.Type.UNION ->
            UnionType(
                schema.types
                    .filter { it.type != Schema.Type.NULL }
                    .map { toAirbyteType(it) }
                    .toSet()
            )
        Schema.Type.NULL ->
            throw IllegalStateException("Null should only appear in union types, and should have been handled in an earlier recursion. This is a bug.")
        else ->
            throw IllegalArgumentException("Unsupported Avro schema $schema")
    }
}
