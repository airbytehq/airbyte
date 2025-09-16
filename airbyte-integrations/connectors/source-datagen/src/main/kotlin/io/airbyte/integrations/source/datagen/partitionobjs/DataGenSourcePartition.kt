package io.airbyte.integrations.source.datagen.partitionobjs

class DataGenSourcePartition(
    val streamState: DataGenStreamState,
    val modulo: Int = 1,
    val offset: Int = 0
)
