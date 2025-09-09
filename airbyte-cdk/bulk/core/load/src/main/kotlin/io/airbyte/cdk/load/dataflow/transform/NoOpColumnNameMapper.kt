package io.airbyte.cdk.load.dataflow.transform

import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Singleton @Secondary class NoOpColumnNameMapper : ColumnNameMapper
