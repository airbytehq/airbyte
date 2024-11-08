/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.avro

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

fun InputStream.toAvroReader(avroSchema: Schema): AvroReader {
    val reader = GenericDatumReader<GenericRecord>(avroSchema)
    val tmpFile =
        kotlin.io.path.createTempFile(
            prefix = "${avroSchema.namespace}.${avroSchema.name}",
            suffix = ".avro"
        )
    tmpFile.outputStream().use { outputStream -> this.copyTo(outputStream) }
    val file = tmpFile.toFile()
    val dataFileReader = DataFileReader(file, reader)
    return AvroReader(dataFileReader, file)
}
