/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.probably_core_stuff

// map from the column name as declared in the schema,
// to the column name that we'll create in the actual table
data class DestinationColumnNameMapping(val columnNameMapping: Map<String, String>) :
    Map<String, String> by columnNameMapping
