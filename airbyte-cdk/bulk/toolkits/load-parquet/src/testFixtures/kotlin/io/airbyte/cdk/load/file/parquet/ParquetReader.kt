/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.parquet

import java.io.Closeable
import java.io.File
import java.io.InputStream
import kotlin.io.path.outputStream
import org.apache.avro.Schema
import org.apache.avro.generic.GenericRecord
import org.apache.hadoop.fs.Path
import org.apache.parquet.avro.AvroParquetReader
import org.apache.parquet.avro.AvroReadSupport
import org.apache.parquet.hadoop.ParquetReader as ApacheParquetReader

class ParquetReader(
    private val reader: ApacheParquetReader<GenericRecord>,
    private val tmpFile: File
) : Closeable {
    private fun read(): GenericRecord? {
        return reader.read()
    }

    fun recordSequence(): Sequence<GenericRecord> = generateSequence { read() }

    override fun close() {
        reader.close()
        tmpFile.delete()
    }
}

fun InputStream.toParquetReader(avroSchema: Schema): ParquetReader {

    val tmpFile =
        kotlin.io.path.createTempFile(
            prefix = "${avroSchema.namespace}.${avroSchema.name}",
            suffix = ".avro"
        )
    tmpFile.outputStream().use { outputStream -> this.copyTo(outputStream) }
    val reader =
        AvroParquetReader.builder<GenericRecord>(
                AvroReadSupport(),
                Path(tmpFile.toAbsolutePath().toString())
            )
            .build()

    return ParquetReader(reader, tmpFile.toFile())
}
