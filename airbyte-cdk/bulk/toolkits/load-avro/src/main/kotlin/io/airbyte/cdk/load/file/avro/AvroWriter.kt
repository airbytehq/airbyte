/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.avro

import io.airbyte.cdk.load.command.avro.AvroCompressionConfiguration
import java.io.Closeable
import java.io.OutputStream
import org.apache.avro.Schema
import org.apache.avro.file.DataFileWriter
import org.apache.avro.generic.GenericDatumWriter
import org.apache.avro.generic.GenericRecord

class AvroWriter(
    private val dataFileWriter: DataFileWriter<GenericRecord>,
) : Closeable {
    fun write(record: GenericRecord) {
        dataFileWriter.append(record)
    }

    fun flush() {
        dataFileWriter.flush()
    }

    override fun close() {
        dataFileWriter.close()
    }
}

fun OutputStream.toAvroWriter(
    avroSchema: Schema,
    config: AvroCompressionConfiguration
): AvroWriter {
    val datumWriter = GenericDatumWriter<GenericRecord>(avroSchema)
    val dataFileWriter = DataFileWriter(datumWriter)
    dataFileWriter.setCodec(config.compressionCodec)
    dataFileWriter.create(avroSchema, this)
    return AvroWriter(dataFileWriter)
}
