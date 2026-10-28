/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DataFile

interface SupersededDataFileProvider {
    fun fullySupersededDataFiles(): Set<DataFile>
}
