/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

data class Column(val columnName: String, val columnTypeName: String, val nullable: Boolean = true)
