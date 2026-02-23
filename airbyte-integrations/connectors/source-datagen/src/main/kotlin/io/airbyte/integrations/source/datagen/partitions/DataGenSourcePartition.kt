/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.partitions

class DataGenSourcePartition(val streamState: DataGenStreamState, val modulo: Int, val offset: Int)
