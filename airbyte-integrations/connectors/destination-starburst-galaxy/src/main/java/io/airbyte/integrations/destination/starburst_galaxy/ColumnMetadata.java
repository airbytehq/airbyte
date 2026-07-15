/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import io.trino.spi.type.Type;

public record ColumnMetadata(String name, Type galaxyIcebergType, int position) {}
