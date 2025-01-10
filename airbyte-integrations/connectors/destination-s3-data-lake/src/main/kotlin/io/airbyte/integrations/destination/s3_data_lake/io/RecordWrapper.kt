/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

import org.apache.iceberg.data.Record

/**
 * Wraps the Iceberg [Record] class to add the potential delta [Operation] associated with the
 * record. All record operations are delegated to the provided [Record] object.
 */
data class RecordWrapper(val delegate: Record, val operation: Operation) : Record by delegate
