/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.data.iceberg.parquet.IcebergObjectMode
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

data class IcebergSchemaOptions(val objectMode: IcebergObjectMode)

@Factory
class IcebergSchemaOptionsFactory {
    @Singleton
    @Secondary
    fun defaultIcebergSchemaOptions() =
        IcebergSchemaOptions(objectMode = IcebergObjectMode.JSON_STRING)
}
