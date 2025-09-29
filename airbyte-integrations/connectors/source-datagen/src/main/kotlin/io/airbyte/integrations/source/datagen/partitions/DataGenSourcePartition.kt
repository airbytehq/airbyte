/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.partitions

class DataGenSourcePartition(val streamState: DataGenStreamState, val modulo: Int, val offset: Int)
