package io.airbyte.cdk.load.write

interface LoadStrategy {
    val inputPartitions: Int get() = 1
}
