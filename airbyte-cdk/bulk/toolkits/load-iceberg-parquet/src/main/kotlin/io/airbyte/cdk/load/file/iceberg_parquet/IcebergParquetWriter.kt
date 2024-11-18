/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.iceberg_parquet

import java.io.Closeable
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.io.DataWriter

class IcebergParquetWriter(private val writer: DataWriter<GenericRecord>) : Closeable {
    fun write(record: GenericRecord) = writer.write(record)
    override fun close() = writer.close()
}
