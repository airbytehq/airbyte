/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.defaults

import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/*
 * Default implementation of the ColumnNameMapper. If your destination needs destination-specific
 * column name mapping, create your own ColumnNameMapper implementation in your destination.
 */
@Singleton @Secondary class NoOpColumnNameMapper : ColumnNameMapper
