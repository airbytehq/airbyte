/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

@Singleton
class BigquerySpecification : ConfigurationSpecification() {
    val option: String = "foo"

    override fun toString(): String {
        return "BigquerySpecification(option='$option')"
    }
}
